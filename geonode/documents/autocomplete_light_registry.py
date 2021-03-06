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

from autocomplete_light.registry import register
from autocomplete_light.autocomplete.shortcuts import AutocompleteModelTemplate
from .models import Document, Event, KnowledgehubDocument, News, Blog


class DocumentAutocomplete(AutocompleteModelTemplate):
    choice_template = 'autocomplete_response.html'

class EventAutocomplete(DocumentAutocomplete):
    choice_template = 'autocomplete_response.html'

class NewsAutocomplete(DocumentAutocomplete):
    choice_template = 'autocomplete_response.html'

class BlogAutocomplete(DocumentAutocomplete):
    choice_template = 'autocomplete_response.html'

class KnowledgehubDocumentAutocomplete(DocumentAutocomplete):
    choice_template = 'autocomplete_response.html'

register(
    Document,
    DocumentAutocomplete,
    search_fields=['title'],
    order_by=['title'],
    limit_choices=100,
    autocomplete_js_attributes={
        'placeholder': 'Document name..',
    },
)

register(
    Event,
    EventAutocomplete,
    search_fields=['title'],
    order_by=['title'],
    limit_choices=100,
    autocomplete_js_attributes={
        'placeholder': 'Event name...',
    },
)

register(
    News,
    NewsAutocomplete,
    search_fields=['title'],
    order_by=['title'],
    limit_choices=100,
    autocomplete_js_attributes={
        'placeholder': 'News name...',
    },
)

register(
    Blog,
    BlogAutocomplete,
    search_fields=['title'],
    order_by=['title'],
    limit_choices=100,
    autocomplete_js_attributes={
        'placeholder': 'Blog name...',
    },
)

register(
    KnowledgehubDocument,
    KnowledgehubDocumentAutocomplete,
    search_fields=['title'],
    order_by=['title'],
    limit_choices=100,
    autocomplete_js_attributes={
        'placeholder': 'Document name...',
    },
)
