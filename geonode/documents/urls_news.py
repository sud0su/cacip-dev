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
from .models import News

js_info_dict = {
    'packages': ('geonode.documents',),
}
basemodel = News
prefix = basemodel.__name__.lower()

urlpatterns = [  # 'geonode.documents.views',
    url(r'^$',
        TemplateView.as_view(
        template_name='documents/document_list.html'),
        {'facet_type': 'documents','basemodel': basemodel},
        name=prefix+'_browse'),
    url(r'^(?P<docid>\d+)/?$',
        views.document_detail, name=prefix+'_detail', kwargs={'basemodel':basemodel}),
    url(r'^(?P<docid>\d+)/download/?$',
        views.document_download, name=prefix+'_download', kwargs={'basemodel':basemodel}),
    url(r'^(?P<docid>\d+)/replace$', login_required(DocumentUpdateView.as_view()),
        name=prefix+"_replace", kwargs={'basemodel':basemodel}),
    url(r'^(?P<docid>\d+)/remove$',
        views.document_remove, name=prefix+"_remove", kwargs={'basemodel':basemodel}),
    url(r'^upload/?$', login_required(
        DocumentUploadView.as_view()), name=prefix+'_upload', kwargs={'basemodel':basemodel}),
    url(r'^search/?$', views.document_search_page,
        name=prefix+'_search_page', kwargs={'basemodel':basemodel}),
    url(r'^(?P<docid>[^/]*)/metadata_detail$', views.document_metadata_detail,
        name=prefix+'_metadata_detail', kwargs={'basemodel':basemodel}),
    url(r'^(?P<docid>\d+)/metadata$',
        views.document_metadata, name=prefix+'_metadata', kwargs={'basemodel':basemodel}),
    url(
        r'^metadata/batch/(?P<ids>[^/]*)/$',
        views.document_batch_metadata,
        name=prefix+'_batch_metadata', kwargs={'basemodel':basemodel}),
    url(r'^(?P<docid>\d+)/metadata_advanced$', views.document_metadata_advanced,
        name=prefix+'_metadata_advanced', kwargs={'basemodel':basemodel}),
    url(r'^(?P<docid>[^/]*)/thumb_upload$',
        views.document_thumb_upload, name=prefix+'_thumb_upload', kwargs={'basemodel':basemodel}),

    # h keywords
    url(r'^h_keywords_api$',
        basemodel.h_keywords_api,
        name=prefix+'__h_keywords_api'),
]
