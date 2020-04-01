# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import os
import json
import logging
from itertools import chain

from guardian.shortcuts import get_perms

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django_downloadview.response import DownloadResponse
from django.views.generic.edit import UpdateView, CreateView
from django.db.models import F
from django.forms.utils import ErrorList

from geonode.utils import resolve_object
from geonode.security.views import _perms_info_json
from geonode.people.forms import ProfileForm
from geonode.base.forms import CategoryForm
from geonode.base.models import TopicCategory
from geonode.documents.models import Document, get_related_resources, Event, News, Blog, KnowledgehubDocument
from geonode.documents.forms import DocumentForm, DocumentCreateForm, DocumentReplaceForm
from geonode.documents.models import IMGTYPES
from geonode.documents.renderers import generate_thumbnail_content, MissingPILError
from geonode.utils import build_social_links
from geonode.groups.models import GroupProfile
from geonode.base.views import batch_modify

# CACIP
from matrix.views import savematrix
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.forms import HiddenInput, TextInput
from geonode.base.forms import ResourceBaseForm, ResourceBaseDateTimePicker

logger = logging.getLogger("geonode.documents.views")

ALLOWED_DOC_TYPES = settings.ALLOWED_DOCUMENT_TYPES

_PERMISSION_MSG_DELETE = _("You are not permitted to delete this document")
_PERMISSION_MSG_GENERIC = _("You do not have permissions for this document.")
_PERMISSION_MSG_MODIFY = _("You are not permitted to modify this document")
_PERMISSION_MSG_METADATA = _(
    "You are not permitted to modify this document's metadata")
_PERMISSION_MSG_VIEW = _("You are not permitted to view this document")


def _resolve_document(request, docid, permission='base.change_resourcebase',
                      msg=_PERMISSION_MSG_GENERIC, basemodel=Document, **kwargs):
    '''
    Resolve the document by the provided primary key and check the optional permission.
    '''
    return resolve_object(request, basemodel, {'pk': docid},
                          permission=permission, permission_msg=msg, **kwargs)


def document_detail(request, docid, basemodel=Document):
    """
    The view that show details of each document
    """
    document = None
    try:
        document = _resolve_document(
            request,
            docid,
            'base.view_resourcebase',
            _PERMISSION_MSG_VIEW,
            basemodel=basemodel)

    except Http404:
        return HttpResponse(
            loader.render_to_string(
                '404.html', context={
                }, request=request), status=404)

    except PermissionDenied:
        return HttpResponse(
            loader.render_to_string(
                '401.html', context={
                    'error_message': _("You are not allowed to view this document.")}, request=request), status=403)

    if document is None:
        return HttpResponse(
            'An unknown error has occured.',
            content_type="text/plain",
            status=401
        )

    else:
        related = get_related_resources(document)

        # Update count for popularity ranking,
        # but do not includes admins or resource owners
        if request.user != document.owner and not request.user.is_superuser:
            Document.objects.filter(
                id=document.id).update(
                popular_count=F('popular_count') + 1)
            savematrix(request=request, action='Document View', resource=document)

        metadata = document.link_set.metadata().filter(
            name__in=settings.DOWNLOAD_FORMATS_METADATA)

        group = None
        if document.group:
            try:
                group = GroupProfile.objects.get(slug=document.group.name)
            except GroupProfile.DoesNotExist:
                group = None
        preview_url = document.thumbnail_url.replace("-thumb", "-preview")
        context_dict = {
            'perms_list': get_perms(
                request.user,
                document.get_self_resource()),
            'permissions_json': _perms_info_json(document),
            'resource': document,
            'group': group,
            'metadata': metadata,
            'imgtypes': IMGTYPES,
            'preview_url':preview_url,
            'related': related}

        if settings.SOCIAL_ORIGINS:
            context_dict["social_links"] = build_social_links(
                request, document)

        if getattr(settings, 'EXIF_ENABLED', False):
            try:
                from geonode.contrib.exif.utils import exif_extract_dict
                exif = exif_extract_dict(document)
                if exif:
                    context_dict['exif_data'] = exif
            except BaseException:
                print "Exif extraction failed."

        return render(
            request,
            "documents/document_detail.html",
            context=context_dict)


def document_download(request, docid, basemodel=Document):
    document = get_object_or_404(basemodel, pk=docid)

    if request.user != document.owner and not request.user.is_superuser:
        savematrix(request=request, action='Document Download', resource=document)

    if settings.MONITORING_ENABLED and document:
        if hasattr(document, 'alternate'):
            request.add_resource('document', document.alternate)

    if not request.user.has_perm(
            'base.download_resourcebase',
            obj=document.get_self_resource()):
        return HttpResponse(
            loader.render_to_string(
                '401.html', context={
                    'error_message': _("You are not allowed to view this document.")}, request=request), status=401)
    return DownloadResponse(document.doc_file)


class DocumentUploadView(CreateView):
    template_name = 'documents/document_upload.html'
    form_class = DocumentCreateForm
    context = {}

    def get_context_data(self, **kwargs):
        context = super(DocumentUploadView, self).get_context_data(**kwargs)
        context['ALLOWED_DOC_TYPES'] = ALLOWED_DOC_TYPES
        context.update(getattr(self, 'context', {}))
        return context

    def form_invalid(self, form):
        if self.request.GET.get('no__redirect', False):
            out = {'success': False}
            out['message'] = ""
            status_code = 400
            return HttpResponse(
                json.dumps(out),
                content_type='application/json',
                status=status_code)
        else:
            form.name = None
            form.title = None
            form.doc_file = None
            form.doc_url = None
            return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        # by default, if RESOURCE_PUBLISHING=True then document.is_published
        # must be set to False
        # RESOURCE_PUBLISHING works in similar way as ADMIN_MODERATE_UPLOADS,
        # but is applied to documents only. ADMIN_MODERATE_UPLOADS has wider
        # usage
        is_published = not (
            settings.RESOURCE_PUBLISHING or settings.ADMIN_MODERATE_UPLOADS)
        self.object.is_published = is_published
        self.object.save()
        form.save_many2many()
        self.object.set_permissions(form.cleaned_data['permissions'])

        abstract = None
        date = None
        regions = []
        keywords = []
        bbox = None

        out = {'success': False}

        if getattr(settings, 'EXIF_ENABLED', False):
            try:
                from geonode.contrib.exif.utils import exif_extract_metadata_doc
                exif_metadata = exif_extract_metadata_doc(self.object)
                if exif_metadata:
                    date = exif_metadata.get('date', None)
                    keywords.extend(exif_metadata.get('keywords', []))
                    bbox = exif_metadata.get('bbox', None)
                    abstract = exif_metadata.get('abstract', None)
            except BaseException:
                print "Exif extraction failed."

        if getattr(settings, 'NLP_ENABLED', False):
            try:
                from geonode.contrib.nlp.utils import nlp_extract_metadata_doc
                nlp_metadata = nlp_extract_metadata_doc(self.object)
                if nlp_metadata:
                    regions.extend(nlp_metadata.get('regions', []))
                    keywords.extend(nlp_metadata.get('keywords', []))
            except BaseException:
                print "NLP extraction failed."

        if abstract:
            self.object.abstract = abstract
            self.object.save()

        if date:
            self.object.date = date
            self.object.date_type = "Creation"
            self.object.save()

        if len(regions) > 0:
            self.object.regions.add(*regions)

        if len(keywords) > 0:
            self.object.keywords.add(*keywords)

        if bbox:
            bbox_x0, bbox_x1, bbox_y0, bbox_y1 = bbox
            Document.objects.filter(id=self.object.pk).update(
                bbox_x0=bbox_x0,
                bbox_x1=bbox_x1,
                bbox_y0=bbox_y0,
                bbox_y1=bbox_y1)

        if getattr(settings, 'SLACK_ENABLED', False):
            try:
                from geonode.contrib.slack.utils import build_slack_message_document, send_slack_message
                send_slack_message(
                    build_slack_message_document(
                        "document_new", self.object))
            except BaseException:
                print "Could not send slack message for new document."

        if settings.MONITORING_ENABLED and self.object:
            if hasattr(self.object, 'alternate'):
                self.request.add_resource('document', self.object.alternate)

        if self.request.GET.get('no__redirect', False):
            out['success'] = True
            out['url'] = reverse(
                'document_detail',
                args=(
                    self.object.id,
                ))
            if out['success']:
                status_code = 200
            else:
                status_code = 400
            return HttpResponse(
                json.dumps(out),
                content_type='application/json',
                status=status_code)
        else:
            return HttpResponseRedirect(
                reverse(
                    self.object.class_name.lower()+'_metadata',
                    args=(
                        self.object.id,
                    )))

class EventCreateForm(DocumentCreateForm):

    event_date_start = forms.DateTimeField(
        label=_("Event Date Start"),
        localize=True,
        input_formats=['%Y-%m-%d %H:%M %p'],
        widget=ResourceBaseDateTimePicker(options={"format": "YYYY-MM-DD HH:mm a"})
    )

    event_date_end = forms.DateTimeField(
        label=_("Event Date End"),
        localize=True,
        input_formats=['%Y-%m-%d %H:%M %p'],
        widget=ResourceBaseDateTimePicker(options={"format": "YYYY-MM-DD HH:mm a"})
    )

    class Meta(DocumentCreateForm.Meta):
        model = Event
        allow_no_doc = True
        fields = ['title', 'doc_url', 'abstract', 'event_date_start', 'event_date_end']
        widgets = dict(DocumentCreateForm.Meta.widgets.items() + {
            'abstract': CKEditorUploadingWidget(),
        }.items())

class NewsCreateForm(DocumentCreateForm):

    def __init__(self, *args, **kwargs):
        super(DocumentCreateForm, self).__init__(*args, **kwargs)
        # self.fields['links'].widget = HiddenInput()
        # self.fields.pop('links', None)

    class Meta(DocumentCreateForm.Meta):
        model = News
        allow_no_doc = True
        fields = ['title', 'abstract']
        widgets = dict(DocumentCreateForm.Meta.widgets.items() + {
            'abstract': CKEditorUploadingWidget(),
            'links': HiddenInput(),
        }.items())

class BlogCreateForm(DocumentCreateForm):

    def __init__(self, *args, **kwargs):
        super(DocumentCreateForm, self).__init__(*args, **kwargs)
        # self.fields['links'].widget = HiddenInput(attrs={'cols': 80, 'rows': 20})
        # self.fields['links'].required = False

    class Meta(DocumentCreateForm.Meta):
        model = Blog
        allow_no_doc = True
        fields = ['title', 'abstract']
        widgets = dict(DocumentCreateForm.Meta.widgets.items() + {
            'abstract': CKEditorUploadingWidget(),
            'links': HiddenInput(),
        }.items())

class KnowledgehubDocumentCreateForm(DocumentCreateForm):
    class Meta(DocumentCreateForm.Meta):
        model = KnowledgehubDocument


class EventUploadView(DocumentUploadView):
    form_class = EventCreateForm

class NewsUploadView(DocumentUploadView):
    form_class = NewsCreateForm

class BlogUploadView(DocumentUploadView):
    form_class = BlogCreateForm

class KnowledgehubDocumentUploadView(DocumentUploadView):
    form_class = KnowledgehubDocumentCreateForm


class DocumentUpdateView(UpdateView):
    template_name = 'documents/document_replace.html'
    pk_url_kwarg = 'docid'
    form_class = DocumentReplaceForm
    queryset = Document.objects.all()
    context_object_name = 'document'
    context = {}

    def get_context_data(self, **kwargs):
        context = super(DocumentUpdateView, self).get_context_data(**kwargs)
        context['ALLOWED_DOC_TYPES'] = ALLOWED_DOC_TYPES
        context.update(getattr(self, 'context', {}))
        return context

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save()
        if settings.MONITORING_ENABLED and self.object:
            if hasattr(self.object, 'alternate'):
                self.request.add_resource('document', self.object.alternate)
        return HttpResponseRedirect(
            reverse(
                self.form_class.Meta.model.namelc()+'_metadata',
                args=(
                    self.object.id,
                )))

class EventReplaceForm(DocumentReplaceForm):
    class Meta(DocumentReplaceForm.Meta):
        model = Event

class NewsReplaceForm(DocumentReplaceForm):
    class Meta(DocumentReplaceForm.Meta):
        model = News

class BlogReplaceForm(DocumentReplaceForm):
    class Meta(DocumentReplaceForm.Meta):
        model = Blog

class KnowledgehubDocumentReplaceForm(DocumentReplaceForm):
    class Meta(DocumentReplaceForm.Meta):
        model = KnowledgehubDocument


class EventUpdateView(DocumentUpdateView):
    form_class = EventReplaceForm
    queryset = Event.objects.all()

class NewsUpdateView(DocumentUpdateView):
    form_class = NewsReplaceForm
    queryset = News.objects.all()

class BlogUpdateView(DocumentUpdateView):
    form_class = BlogReplaceForm
    queryset = Blog.objects.all()

class KnowledgehubDocumentUpdateView(DocumentUpdateView):
    form_class = KnowledgehubDocumentReplaceForm
    queryset = KnowledgehubDocument.objects.all()


@login_required
def document_metadata(
        request,
        docid,
        template='documents/document_metadata.html',
        ajax=True, 
        basemodel=Document):

    document = None
    try:
        document = _resolve_document(
            request,
            docid,
            'base.change_resourcebase_metadata',
            _PERMISSION_MSG_METADATA,
            basemodel=basemodel)

    except Http404:
        return HttpResponse(
            loader.render_to_string(
                '404.html', context={
                }, request=request), status=404)

    except PermissionDenied:
        return HttpResponse(
            loader.render_to_string(
                '401.html', context={
                    'error_message': _("You are not allowed to edit this document.")}, request=request), status=403)

    if document is None:
        return HttpResponse(
            'An unknown error has occured.',
            content_type="text/plain",
            status=401
        )

    else:
        poc = document.poc
        metadata_author = document.metadata_author
        topic_category = document.category
        if hasattr(basemodel, 'form_class'):
            module_path = basemodel.form_class.split('.')
            import_class = module_path.pop()
            basemodel_form = getattr(__import__('.'.join(module_path), fromlist=['']), import_class)
        else:
            basemodel_form = DocumentForm

        if request.method == "POST":
            document_form = basemodel_form(
                request.POST,
                instance=document,
                prefix="resource")
            category_form = CategoryForm(request.POST, prefix="category_choice_field", initial=int(
                request.POST["category_choice_field"]) if request.POST.get("category_choice_field") else None)
        else:
            document_form = basemodel_form(instance=document, prefix="resource")
            category_form = CategoryForm(
                prefix="category_choice_field",
                initial=topic_category.id if topic_category else None)

        if request.method == "POST": 
            if document_form.is_valid() and category_form.is_valid():
                new_poc = document_form.cleaned_data['poc']
                new_author = document_form.cleaned_data['metadata_author']
                new_keywords = document_form.cleaned_data['keywords']
                new_regions = document_form.cleaned_data['regions']
                new_category = TopicCategory.objects.get(
                    id=category_form.cleaned_data['category_choice_field'])

                if new_poc is None:
                    if poc is None:
                        poc_form = ProfileForm(
                            request.POST,
                            prefix="poc",
                            instance=poc)
                    else:
                        poc_form = ProfileForm(request.POST, prefix="poc")
                    if poc_form.is_valid():
                        if len(poc_form.cleaned_data['profile']) == 0:
                            # FIXME use form.add_error in django > 1.7
                            errors = poc_form._errors.setdefault(
                                'profile', ErrorList())
                            errors.append(
                                _('You must set a point of contact for this resource'))
                            poc = None
                    if poc_form.has_changed and poc_form.is_valid():
                        new_poc = poc_form.save()

                if new_author is None:
                    if metadata_author is None:
                        author_form = ProfileForm(request.POST, prefix="author",
                                                instance=metadata_author)
                    else:
                        author_form = ProfileForm(request.POST, prefix="author")
                    if author_form.is_valid():
                        if len(author_form.cleaned_data['profile']) == 0:
                            # FIXME use form.add_error in django > 1.7
                            errors = author_form._errors.setdefault(
                                'profile', ErrorList())
                            errors.append(
                                _('You must set an author for this resource'))
                            metadata_author = None
                    if author_form.has_changed and author_form.is_valid():
                        new_author = author_form.save()

                the_document = document_form.instance
                if new_poc is not None and new_author is not None:
                    the_document.poc = new_poc
                    the_document.metadata_author = new_author
                if new_keywords:
                    the_document.keywords.clear()
                    the_document.keywords.add(*new_keywords)
                if new_regions:
                    the_document.regions.clear()
                    the_document.regions.add(*new_regions)
                the_document.save()
                document_form.save_many2many()
                Document.objects.filter(
                    id=the_document.id).update(
                    category=new_category)

                if getattr(settings, 'SLACK_ENABLED', False):
                    try:
                        from geonode.contrib.slack.utils import build_slack_message_document, send_slack_messages
                        send_slack_messages(
                            build_slack_message_document(
                                "document_edit", the_document))
                    except BaseException:
                        print "Could not send slack message for modified document."

                if not ajax:
                    return HttpResponseRedirect(
                        reverse(
                            document.class_name.lower()+'_detail',
                            args=(
                                document.id,
                            )))

                message = document.id

                return HttpResponse(json.dumps({'message': message}))

            else:
                
                errors = {}
                errors.update(document_form.errors)
                errors.update({'category': category_form.errors})

                return HttpResponse(
                    content = json.dumps({'errors': errors}),
                    status = 500,
                    content_type = 'application/json'
                )


        # - POST Request Ends here -

        # Request.GET
        if poc is not None:
            document_form.fields['poc'].initial = poc.id
            poc_form = ProfileForm(prefix="poc")
            poc_form.hidden = True

        if metadata_author is not None:
            document_form.fields['metadata_author'].initial = metadata_author.id
            author_form = ProfileForm(prefix="author")
            author_form.hidden = True

        metadata_author_groups = []
        if request.user.is_superuser or request.user.is_staff:
            metadata_author_groups = GroupProfile.objects.all()
        else:
            try:
                all_metadata_author_groups = chain(
                    request.user.group_list_all(),
                    GroupProfile.objects.exclude(
                        access="private").exclude(access="public-invite"))
            except BaseException:
                all_metadata_author_groups = GroupProfile.objects.exclude(
                    access="private").exclude(access="public-invite")
            [metadata_author_groups.append(item) for item in all_metadata_author_groups
                if item not in metadata_author_groups]

        if settings.ADMIN_MODERATE_UPLOADS:
            if not request.user.is_superuser:
                document_form.fields['is_published'].widget.attrs.update(
                    {'disabled': 'true'})

                can_change_metadata = request.user.has_perm(
                    'change_resourcebase_metadata',
                    document.get_self_resource())
                try:
                    is_manager = request.user.groupmember_set.all().filter(role='manager').exists()
                except BaseException:
                    is_manager = False
                if not is_manager or not can_change_metadata:
                    document_form.fields['is_approved'].widget.attrs.update(
                        {'disabled': 'true'})

        return render(request, template, context={
            "resource": document,
            "document": document,
            "document_form": document_form,
            "poc_form": poc_form,
            "author_form": author_form,
            "category_form": category_form,
            "metadata_author_groups": metadata_author_groups,
            "GROUP_MANDATORY_RESOURCES": getattr(settings, 'GROUP_MANDATORY_RESOURCES', False),
        })


@login_required
def document_metadata_advanced(request, docid, basemodel=Document):
    return document_metadata(
        request,
        docid,
        template='documents/document_metadata_advanced.html',
        basemodel=basemodel)


@login_required
def document_thumb_upload(
        request,
        docid,
        template='documents/document_thumb_upload.html', 
        basemodel=Document):
    document = None
    try:
        document = _resolve_document(
            request,
            docid,
            'base.change_resourcebase',
            _PERMISSION_MSG_MODIFY,
            basemodel=basemodel)

    except Http404:
        return HttpResponse(
            loader.render_to_string(
                '404.html', context={
                }, request=request), status=404)

    except PermissionDenied:
        return HttpResponse(
            loader.render_to_string(
                '401.html', context={
                    'error_message': _("You are not allowed to edit this document.")}, request=request), status=403)

    if document is None:
        return HttpResponse(
            'An unknown error has occured.',
            content_type="text/plain",
            status=401
        )

    site_url = settings.SITEURL.rstrip('/') if settings.SITEURL.startswith('http') else settings.SITEURL
    if request.method == 'GET':
        return render(request, template, context={
            "resource": document,
            "docid": docid,
            'SITEURL': site_url
        })
    elif request.method == 'POST':
        status_code = 401
        out = {'success': False}
        if docid and request.FILES:
            data = request.FILES.get('base_file')
            if data:
                filename = 'document-{}-thumb.png'.format(document.uuid)
                path = default_storage.save(
                    'tmp/' + filename, ContentFile(data.read()))
                f = os.path.join(settings.MEDIA_ROOT, path)
                try:
                    image_path = f
                except BaseException:
                    image_path = document.find_placeholder()

                thumbnail_content = None
                try:
                    thumbnail_content = generate_thumbnail_content(image_path)
                except MissingPILError:
                    logger.error(
                        'Pillow not installed, could not generate thumbnail.')

                if not thumbnail_content:
                    logger.warning("Thumbnail for document #{} empty.".format(docid))
                document.save_thumbnail(filename, thumbnail_content)
                logger.debug(
                    "Thumbnail for document #{} created.".format(docid))
            status_code = 200
            out['success'] = True
            out['resource'] = docid
        else:
            out['success'] = False
            out['errors'] = 'An unknown error has occured.'
        out['url'] = reverse(
            'document_detail', args=[
                docid])
        return HttpResponse(
            json.dumps(out),
            content_type='application/json',
            status=status_code)


def document_search_page(request):
    # for non-ajax requests, render a generic search page

    if request.method == 'GET':
        params = request.GET
    elif request.method == 'POST':
        params = request.POST
    else:
        return HttpResponse(status=405)

    return render(
        request,
        'documents/document_search.html',
        context={'init_search': json.dumps(params or {}), "site": settings.SITEURL})


@login_required
def document_remove(request, docid, template='documents/document_remove.html', basemodel=Document):
    try:
        document = _resolve_document(
            request,
            docid,
            'base.delete_resourcebase',
            _PERMISSION_MSG_DELETE,
            basemodel=basemodel)

        if request.method == 'GET':
            return render(request, template, context={
                "document": document
            })

        if request.method == 'POST':

            if getattr(settings, 'SLACK_ENABLED', False):
                slack_message = None
                try:
                    from geonode.contrib.slack.utils import build_slack_message_document
                    slack_message = build_slack_message_document(
                        "document_delete", document)
                except BaseException:
                    print "Could not build slack message for delete document."

                document.delete()

                try:
                    from geonode.contrib.slack.utils import send_slack_messages
                    send_slack_messages(slack_message)
                except BaseException:
                    print "Could not send slack message for delete document."
            else:
                document.delete()

            return HttpResponseRedirect(reverse(basemodel.namelc()+"_browse"))
        else:
            return HttpResponse("Not allowed", status=403)

    except PermissionDenied:
        return HttpResponse(
            'You are not allowed to delete this document',
            content_type="text/plain",
            status=401
        )


def document_metadata_detail(
        request,
        docid,
        template='documents/document_metadata_detail.html', 
        basemodel=Document):
    document = _resolve_document(
        request,
        docid,
        'view_resourcebase',
        _PERMISSION_MSG_METADATA,
        basemodel=basemodel)
    group = None
    if document.group:
        try:
            group = GroupProfile.objects.get(slug=document.group.name)
        except GroupProfile.DoesNotExist:
            group = None
    site_url = settings.SITEURL.rstrip('/') if settings.SITEURL.startswith('http') else settings.SITEURL
    return render(request, template, context={
        "resource": document,
        "group": group,
        'SITEURL': site_url
    })


@login_required
def document_batch_metadata(request, ids, basemodel=Document):
    return batch_modify(request, ids, 'Document')
