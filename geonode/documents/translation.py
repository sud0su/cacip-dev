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

from modeltranslation.translator import translator, TranslationOptions
from geonode.documents.models import Document, Event, News, Blog, KnowledgehubDocument


class DocumentTranslationOptions(TranslationOptions):
    # fields = (
    #     'title',
    #     'abstract',
    #     'purpose',
    #     'constraints_other',
    #     'supplemental_information',
    #     'data_quality_statement',
    # )
    fields = ()

class EventTranslationOptions(TranslationOptions):
    fields = ()

class NewsTranslationOptions(TranslationOptions):
    fields = ()

class BlogTranslationOptions(TranslationOptions):
    fields = ()

class KnowledgehubDocumentTranslationOptions(TranslationOptions):
    fields = ()

translator.register(Document, DocumentTranslationOptions)
translator.register(Event, EventTranslationOptions)
translator.register(News, NewsTranslationOptions)
translator.register(Blog, BlogTranslationOptions)
translator.register(KnowledgehubDocument, NewsTranslationOptions)
