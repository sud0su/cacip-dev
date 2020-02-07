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

import logging
import os
import uuid
from urlparse import urlparse

from django.db import models
from django.db.models import signals
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.urlresolvers import reverse
from django.contrib.staticfiles import finders
from django.utils.translation import ugettext_lazy as _

from geonode.layers.models import Layer
from geonode.base.models import ResourceBase, resourcebase_post_save, Link
from geonode.documents.enumerations import DOCUMENT_TYPE_MAP, DOCUMENT_MIMETYPE_MAP, DOCUMENT_TYPE_SUBJECTS
from geonode.maps.signals import map_changed_signal
from geonode.maps.models import Map
from geonode.security.utils import remove_object_permissions

# CACIP
from django.core import serializers
from django.db.models import F, Count
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.timezone import now
from geonode.base.models import TaggedContentItem, _HierarchicalTagManager
from taggit.managers import TaggableManager, _TaggableManager
from taggit.models import GenericTaggedItemBase, TagBase

import json

IMGTYPES = ['jpg', 'jpeg', 'tif', 'tiff', 'png', 'gif']

logger = logging.getLogger(__name__)

class AuthorsTag(TagBase):
    pass

class AuthorsTaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(AuthorsTag)

class Document(ResourceBase):

    """
    A document is any kind of information that can be attached to a map such as pdf, images, videos, xls...
    """

    _class_label = _('Document')
    doc_type_help_text = _('Document Type')

    doc_file = models.FileField(upload_to='documents',
                                null=True,
                                blank=True,
                                max_length=255,
                                verbose_name=_('File'))

    extension = models.CharField(max_length=255, blank=True, null=True)

    # add custom field
    version    = models.CharField(max_length=50, blank=True, null=True)
    papersize  = models.CharField(max_length=2, blank=True, null=True)
    datasource = models.CharField(max_length=128, blank=True, null=True)
    subtitle = models.CharField(max_length=128, blank=True, null=True)

    # CACIP
    source_id = models.CharField(max_length=128, blank=True, null=True)
    sourcetext = models.TextField(blank=True, null=True)
    creators = TaggableManager(
        _('creators'),
        through=AuthorsTaggedItem,
        blank=True,
        help_text='creators'
    )

    # doc_type = models.CharField(max_length=128, blank=True, null=True)
    doc_type = models.CharField(
        _('Document Type'),
        max_length=128,
        choices=DOCUMENT_TYPE_SUBJECTS,
        default='publications',
        help_text=doc_type_help_text)

    doc_url = models.URLField(
        blank=True,
        null=True,
        max_length=512,
        help_text=_('The URL of the document if it is external.'),
        verbose_name=_('URL'))

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        # return reverse('document_detail', args=(self.id,))
        return reverse(self.__class__.__name__.lower()+'_detail', args=(self.id,))

    @property
    def name_long(self):
        if not self.title:
            return str(self.id)
        else:
            return '%s (%s)' % (self.title, self.id)

    @property
    def class_label(self):
        return _(getattr(self, '_class_label', self.__class__.__name__))

    def find_placeholder(self):
        placeholder = 'documents/{0}-placeholder.png'
        return finders.find(placeholder.format(self.extension), False) or \
            finders.find(placeholder.format('generic'), False)

    def is_file(self):
        return self.doc_file and self.extension

    def is_image(self):
        return self.is_file() and self.extension.lower() in IMGTYPES

    @property
    def class_name(self):
        return self.__class__.__name__

    @classmethod
    def cm_class_name(cls, *args, **kwargs):
        return getattr(cls, '__name__', 'Document')

    @classmethod
    def namelc(cls, *args, **kwargs):
        return cls.cm_class_name().lower()

    @classmethod
    def h_keywords_api(cls, *args, **kwargs):
        
        # keywords = cls.objects.annotate(
        #     text=F('keywords__name'),
        #     href=F('keywords__slug'),
        # ).values(
        #     'text', 
        #     'href'
        # ).annotate(
        #     # put in separate annotate after values() to avoid 
        #     # ValueError: The annotation 'id' conflicts with a field on the model.
        #     id=F('keywords__id') 
        # ).order_by(
        #     'text'
        # )
        
        keywords = cls.objects.values(
            'keywords__name', 
            'keywords__slug'
        ).annotate(
            count=Count('keywords__name'),
        ).order_by(
            'keywords__name'
        ).exclude(
            keywords__name__isnull=True
        )
        renamed = [{'text':k['keywords__name'], 'href':k['keywords__slug']} for k in keywords]
        return HttpResponse(
            content=json.dumps(renamed), 
            content_type='application/json'
        )

    class Meta(ResourceBase.Meta):
        pass


class DocumentResourceLink(models.Model):

    # relation to the document model
    document = models.ForeignKey(Document, related_name='links')

    # relation to the resource model
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    resource = GenericForeignKey('content_type', 'object_id')


class Event(Document):

    _class_label = _('Event')
    form_class = 'geonode.documents.forms.EventForm'
    
    event_date_start = models.DateTimeField(
        _('Event date start'),
        # default=now,
        blank=True,
        null=True,
        help_text='Event date start')
    event_date_end = models.DateTimeField(
        _('Event date end'),
        # default=now,
        blank=True,
        null=True,
        help_text='Event date end')

    # def get_absolute_url(self):
    #     return reverse(self.__class__.__name__.lower()+'_detail', args=(self.id,))

class News(Document):

    _class_label = _('News')
    form_class = 'geonode.documents.forms.NewsForm'
    
    # def get_absolute_url(self):
    #     return reverse(self.__class__.__name__.lower()+'_detail', args=(self.id,))

class Blog(Document):

    _class_label = _('Blog')
    form_class = 'geonode.documents.forms.BlogForm'
    
    # def get_absolute_url(self):
    #     return reverse(self.__class__.__name__.lower()+'_detail', args=(self.id,))

class KnowledgehubDocument(Document):

    _class_label = _('Document')
    form_class = 'geonode.documents.forms.KnowledgehubDocumentForm'

    # def get_absolute_url(self):
    #     return reverse(self.__class__.__name__.lower()+'_detail', args=(self.id,))


def get_related_documents(resource):
    if isinstance(resource, Layer) or isinstance(resource, Map):
        content_type = ContentType.objects.get_for_model(resource)
        return Document.objects.filter(links__content_type=content_type,
                                       links__object_id=resource.pk)
    else:
        return None


def get_related_resources(document):
    if document.links:
        try:
            return [
                link.content_type.get_object_for_this_type(id=link.object_id)
                for link in document.links.all()
            ]
        except BaseException:
            return []
    else:
        return []


def pre_save_document(instance, sender, **kwargs):
    base_name, extension, doc_type = None, None, None

    if instance.doc_file:
        base_name, extension = os.path.splitext(instance.doc_file.name)
        instance.extension = extension[1:]
        doc_type_map = DOCUMENT_TYPE_MAP
        doc_type_map.update(getattr(settings, 'DOCUMENT_TYPE_MAP', {}))
        if doc_type_map is None:
            doc_type = 'other'
        else:
            doc_type = doc_type_map.get(instance.extension, 'other')
        # is default doc_type
        if instance.doc_type != type(instance)._meta.get_field('doc_type').get_default():
            instance.doc_type = doc_type

    elif instance.doc_url:
        if '.' in urlparse(instance.doc_url).path:
            instance.extension = urlparse(instance.doc_url).path.rsplit('.')[-1]

    if hasattr(instance, 'class_label'):
        # is default doc_type
        if instance.doc_type == type(instance)._meta.get_field('doc_type').get_default():
            instance.doc_type = instance.class_label

    if not instance.uuid:
        instance.uuid = str(uuid.uuid1())
    instance.csw_type = 'document'

    if instance.abstract == '' or instance.abstract is None:
        instance.abstract = 'No abstract provided'

    if instance.title == '' or instance.title is None:
        instance.title = instance.doc_file.name

    resources = get_related_resources(instance)

    if resources:
        instance.bbox_x0 = min([r.bbox_x0 for r in resources])
        instance.bbox_x1 = max([r.bbox_x1 for r in resources])
        instance.bbox_y0 = min([r.bbox_y0 for r in resources])
        instance.bbox_y1 = max([r.bbox_y1 for r in resources])
    else:
        instance.bbox_x0 = -180
        instance.bbox_x1 = 180
        instance.bbox_y0 = -90
        instance.bbox_y1 = 90


def post_save_document(instance, *args, **kwargs):

    name = None
    ext = instance.extension
    mime_type_map = DOCUMENT_MIMETYPE_MAP
    mime_type_map.update(getattr(settings, 'DOCUMENT_MIMETYPE_MAP', {}))
    mime = mime_type_map.get(ext, 'text/plain')
    url = None

    if instance.doc_file:
        name = "Hosted Document"
        site_url = settings.SITEURL.rstrip('/') if settings.SITEURL.startswith('http') else settings.SITEURL
        url = '%s%s' % (
            site_url,
            reverse('document_download', args=(instance.id,)))
    elif instance.doc_url:
        name = "External Document"
        url = instance.doc_url

    if name and url and ext:
        Link.objects.get_or_create(
            resource=instance.resourcebase_ptr,
            url=url,
            defaults=dict(
                extension=ext,
                name=name,
                mime=mime,
                url=url,
                link_type='data',))


def create_thumbnail(sender, instance, created, **kwargs):
    from .tasks import create_document_thumbnail

    create_document_thumbnail.delay(object_id=instance.id)


def update_documents_extent(sender, **kwargs):
    documents = get_related_documents(sender)
    if documents:
        for document in documents:
            document.save()


def pre_delete_document(instance, sender, **kwargs):
    remove_object_permissions(instance.get_self_resource())


signals.pre_save.connect(pre_save_document, sender=Document)
signals.post_save.connect(create_thumbnail, sender=Document)
signals.post_save.connect(post_save_document, sender=Document)
signals.post_save.connect(resourcebase_post_save, sender=Document)
signals.pre_delete.connect(pre_delete_document, sender=Document)
map_changed_signal.connect(update_documents_extent)

signals.pre_save.connect(pre_save_document, sender=Event)
signals.post_save.connect(create_thumbnail, sender=Event)
signals.post_save.connect(post_save_document, sender=Event)
signals.post_save.connect(resourcebase_post_save, sender=Event)
signals.pre_delete.connect(pre_delete_document, sender=Event)
map_changed_signal.connect(update_documents_extent)

signals.pre_save.connect(pre_save_document, sender=News)
signals.post_save.connect(create_thumbnail, sender=News)
signals.post_save.connect(post_save_document, sender=News)
signals.post_save.connect(resourcebase_post_save, sender=News)
signals.pre_delete.connect(pre_delete_document, sender=News)
map_changed_signal.connect(update_documents_extent)

signals.pre_save.connect(pre_save_document, sender=Blog)
signals.post_save.connect(create_thumbnail, sender=Blog)
signals.post_save.connect(post_save_document, sender=Blog)
signals.post_save.connect(resourcebase_post_save, sender=Blog)
signals.pre_delete.connect(pre_delete_document, sender=Blog)
map_changed_signal.connect(update_documents_extent)

signals.pre_save.connect(pre_save_document, sender=KnowledgehubDocument)
signals.post_save.connect(create_thumbnail, sender=KnowledgehubDocument)
signals.post_save.connect(post_save_document, sender=KnowledgehubDocument)
signals.post_save.connect(resourcebase_post_save, sender=KnowledgehubDocument)
signals.pre_delete.connect(pre_delete_document, sender=KnowledgehubDocument)
map_changed_signal.connect(update_documents_extent)
