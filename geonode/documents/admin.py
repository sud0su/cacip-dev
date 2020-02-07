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

from django.contrib import admin
from geonode.documents.models import Document, Event, News, Blog, KnowledgehubDocument
from geonode.base.admin import MediaTranslationAdmin, ResourceBaseAdminForm
from geonode.base.admin import metadata_batch_edit

from django import forms
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class DocumentAdminForm(ResourceBaseAdminForm):

    class Meta:
        model = Document
        fields = '__all__'
        exclude = (
            'uuid',
            'resource',
        )

class EventAdminForm(DocumentAdminForm):

    class Meta(DocumentAdminForm.Meta):
        model = Event

class KnowledgehubDocumentAdminForm(DocumentAdminForm):

    class Meta(DocumentAdminForm.Meta):
        model = KnowledgehubDocument

class NewsAdminForm(DocumentAdminForm):

    class Meta(DocumentAdminForm.Meta):
        model = News

class BlogAdminForm(DocumentAdminForm):

    def __init__(self, *args, **kwargs):
        super(BlogAdminForm, self).__init__(*args, **kwargs)

        # self.fields['title'].widget = admin.widgets.AdminTextInputWidget
        self.fields['title_en'].widget = admin.widgets.AdminTextInputWidget()
        self.fields['abstract_en'].widget = CKEditorUploadingWidget()

    class Meta(DocumentAdminForm.Meta):
        model = Blog
        widgets = {
            # 'title_en': admin.widgets.AdminTextInputWidget,
            # 'abstract_en': CKEditorUploadingWidget(),
            # 'abstract_ru': CKEditorUploadingWidget(),
            # 'abstract_en': TinyMCE(attrs={'cols': 100, 'rows': 10}),
            # 'abstract_en': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        }


class DocumentAdmin(MediaTranslationAdmin):
    list_display = ('id',
                    'title',
                    'date',
                    'category',
                    'group',
                    'is_approved',
                    'is_published',
                    'metadata_completeness')
    list_display_links = ('id',)
    list_editable = ('title', 'category', 'group', 'is_approved', 'is_published')
    list_filter = ('date', 'date_type', 'category', 'group', 'is_approved', 'is_published', 
        'datasource', 'input_method', 'restriction_code_type')
    search_fields = ('title', 'abstract', 'purpose',
                     'is_approved', 'is_published',)
    date_hierarchy = 'date'
    form = DocumentAdminForm
    actions = [metadata_batch_edit]

class EventAdmin(DocumentAdmin):
    form = EventAdminForm

class NewsAdmin(DocumentAdmin):
    form = NewsAdminForm

class BlogAdmin(DocumentAdmin):
    form = BlogAdminForm

class KnowledgehubDocumentAdmin(DocumentAdmin):
    form = KnowledgehubDocumentAdminForm

admin.site.register(Document, DocumentAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(KnowledgehubDocument, KnowledgehubDocumentAdmin)
