# -*- coding: utf-8 -*-
#
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
#

from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from .views import DocumentUploadView, DocumentUpdateView
from . import views
from .models import KHDocument

js_info_dict = {
    'packages': ('geonode.documents',),
}

urlpatterns = [  # 'geonode.documents.views',
    url(r'^$',
        TemplateView.as_view(
        template_name='documents/document_list.html'),
        {'facet_type': 'documents','basemodel': 'KHDocument'},
        name='khdocument_browse'),
    url(r'^(?P<docid>\d+)/?$',
        views.document_detail, name='khdocument_detail', kwargs={'basemodel':KHDocument}),
    url(r'^(?P<docid>\d+)/download/?$',
        views.document_download, name='khdocument_download', kwargs={'basemodel':KHDocument}),
    url(r'^(?P<docid>\d+)/replace$', login_required(DocumentUpdateView.as_view()),
        name="khdocument_replace", kwargs={'basemodel':KHDocument}),
    url(r'^(?P<docid>\d+)/remove$',
        views.document_remove, name="khdocument_remove", kwargs={'basemodel':KHDocument}),
    url(r'^upload/?$', login_required(
        DocumentUploadView.as_view()), name='khdocument_upload', kwargs={'basemodel':KHDocument}),
    url(r'^search/?$', views.document_search_page,
        name='khdocument_search_page', kwargs={'basemodel':KHDocument}),
    url(r'^(?P<docid>[^/]*)/metadata_detail$', views.document_metadata_detail,
        name='khdocument_metadata_detail', kwargs={'basemodel':KHDocument}),
    url(r'^(?P<docid>\d+)/metadata$',
        views.document_metadata, name='khdocument_metadata', kwargs={'basemodel':KHDocument}),
    url(
        r'^metadata/batch/(?P<ids>[^/]*)/$',
        views.document_batch_metadata,
        name='khdocument_batch_metadata', kwargs={'basemodel':KHDocument}),
    url(r'^(?P<docid>\d+)/metadata_advanced$', views.document_metadata_advanced,
        name='khdocument_metadata_advanced', kwargs={'basemodel':KHDocument}),
    url(r'^(?P<docid>[^/]*)/thumb_upload$',
        views.document_thumb_upload, name='khdocument_thumb_upload', kwargs={'basemodel':KHDocument}),
]