from __future__ import division

import base64
import copy
import datetime
import logging
import math
import os
import re
import uuid
import subprocess
import select
import tempfile
import tarfile
import time
import shutil
import string
import httplib2
import urlparse
import urllib
import gc
import weakref
import traceback

from contextlib import closing
from zipfile import ZipFile, is_zipfile, ZIP_DEFLATED
from StringIO import StringIO
from osgeo import ogr
from slugify import Slugify

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
# use lazy gettext because some translated strings are used before
# i18n infra is up
from django.utils.translation import ugettext_lazy as _
from django.db import models, connection, transaction
from django.contrib.gis.geos import GEOSGeometry
from django.core.serializers.json import DjangoJSONEncoder

from geonode import geoserver, qgis_server  # noqa

try:
    import json
except ImportError:
    from django.utils import simplejson as json

# EPR
from django.db.models.expressions import RawSQL
from django.db.models.query import QuerySet
from itertools import izip
# from graphos.renderers.base import BaseChart

import sys

class RawSQL_nogroupby(RawSQL):
    '''Perform RawSQL without include them to group by'''
    contains_aggregate = True
    def get_group_by_cols(self):
        # print 'RawSQL_nogroupby:get_group_by_cols'
        return []

def include_section(section, includes, excludes):
    """
    check whether section is included or not
    defaults to include all
    empty string is valid section name, duplicate section name is valid
    ex: includes=[], excludes=[] == include all
    ex: includes=[], excludes=['section1'] == include all except 'section1'
    ex: includes=['section1'], excludes=[] == exclude all except 'section1'
    """
    if isinstance(section, list):
        return any([include_section(s, includes, excludes) for s in section])
    else:
        return (not includes and not excludes) or \
        (includes and (section in includes)) or \
        (excludes and (section not in excludes))

def none_to_zero(data, zero=0.0):
    '''
    recursively convert data from None to zero
    accept queryset, list, dict, and basic data types
    caution for queryset: will traverse all related table (valuesqueryset is fine)
    '''
    if data is None:
        # return float('NaN')
        return zero
    elif (isinstance(data, models.Model)):
        return {item.name: none_to_zero(getattr(data, item.name)) for item in data._meta.fields}
        # TODO: for string data type return empty string
    elif (isinstance(data, list)) or (isinstance(data, QuerySet)):
        return [none_to_zero(item) for item in data]
    elif isinstance(data, dict):
        d = {key: none_to_zero(item) for key, item in data.items()}
        try:
            d = dict_ext(d) if type(data) == dict_ext else d
        except Exception as e:
            pass
        return d
    else:
        return data

def query_to_dicts(cursor, query_string, *query_args):
    """Run a simple query and produce a generator
    that returns the results as a bunch of dictionaries
    with keys for the column values selected.
    """
    cursor.execute(query_string, query_args)
    col_names = [desc[0] for desc in cursor.description]
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        row_dict = dict(izip(col_names, row))
        yield row_dict
    return

# class ComboChart(BaseChart):
#     def get_template(self):
#         return "graphos/gchart/combo_chart.html"

def multi_to_single_dict(response):
    '''
    Conver dictionary tree to single dimension dictionary
    All dictionary keys in the tree needs to be unique otherwise overwritten
    '''
    if isinstance(response, dict):
        for key, val in response.items():
            if isinstance(val, dict):
                del response[key]
                response.update(multi_to_single_dict(val))

    return response

def merge_dict(dict_a, dict_b):
    '''
    merge multi level dictionary dict_b to dict_a
    '''
    for key in dict_b:
        if isinstance(dict_a.get(key), dict) and isinstance(dict_b.get(key), dict):
            dict_a[key] = merge_dict(dict_a.get(key), dict_b.get(key))
        else:
            dict_a[key] = dict_b[key]
    return dict_a

class dict_wrapper(dict):
    '''
    dummy class based on dict builtin types
    created to simplify accessing deep dict child, eg:
        a = dict_wrapper()
        a.update({1:{2:{3:{}}}})
        with a[1][2][3] as b:
    '''
    def __enter__(self):
        pass
    def __exit__(self, exc_type, exc_value, traceback):
        pass

def div_by_zero_is_zero(a, b):
    try:
        return a/b
    except ZeroDivisionError:
        return 0

def get_percent(a, b):
    return div_by_zero_is_zero(a, b)*100
    
class dict_ext(dict):

    '''
    support for 'with' statement
    '''
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        return

    '''
    get or set multi level sub dictionary
    for assigning, do last level:
        dict_ext_object.path('level1','level2')['level3'] = value
    otherwise:
        SyntaxError: can't assign to function call
    '''
    def path(self, *args):
        d = self
        for arg in args:
            d[arg] = d.setdefault(arg, dict_ext())
            d[arg] = dict_ext(d[arg]) if type(d[arg]) == dict else d[arg]
            d = d[arg]
        return d

    '''
    get multi level sub dictionary
    '''
    def pathget(self, *args):
        d = self
        for arg in args:
            d = d.get(arg, dict_ext({}))
        return d

    '''
    return copy of self with selected keys removed
    '''
    def without(self, *keys):
        return dict_ext({k:v for k,v in self.items() if k not in keys})

    '''
    return copy of self with selected keys only
    '''
    def within(self, *keys):
        return dict_ext({k:self[k] for k in keys if k in self})

    '''
    return self after update
    '''
    def updateget(self, updatedict):
        self.update(updatedict)
        return self

    def valueslistbykey(self, keys, addkeyasattr=False):
        response = []
        for k in keys:
            if k in self:
                if addkeyasattr:
                    self[k]['key'] = k
                response.append(self[k])
        return response

    def containall(self, *keys):
        return all(map(lambda key: key in self, keys))

    def containany(self, *keys):
        return any(map(lambda key: key in self, keys))

    def getkeyfromvalue(self, value):
        return {v: k for k, v in self.items()}[value]

class list_ext(list):

    '''
    similar to 'get' method in dictionary
    '''
    def get(self, idx, defaultval=None):
        if not self:
            return defaultval
        return self[idx] if abs(idx) < len(self) else defaultval

    '''
    return copy of self with values removed
    '''
    def without(self, values=[]):
        return [i for i in self if i not in values]

def set_query_parameter(url, param_name, param_value):
    """Given a URL, set or replace a query parameter and return the
    modified URL.

    >>> set_query_parameter('http://example.com?foo=bar&biz=baz', 'foo', 'stuff')
    'http://example.com?foo=stuff&biz=baz'

    """
    scheme, netloc, path, query_string, fragment = urlparse.urlsplit(url)
    query_params = urlparse.parse_qs(query_string)

    query_params[param_name] = [param_value]
    new_query_string = urllib.urlencode(query_params, doseq=True)

    return urlparse.urlunsplit((scheme, netloc, path, new_query_string, fragment))

class JSONEncoderCustom(json.JSONEncoder):
    def default(self, obj):
        if obj.__class__.__name__ in ["GeoValuesQuerySet", 'ValuesQuerySet']:
            return list(obj)
        elif obj.__class__.__name__ == "date":
            return obj.strftime("%Y-%m-%d")
        elif obj.__class__.__name__ == "datetime":
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif obj.__class__.__name__ == "Decimal":
            return float(obj)
        else:
            msg = 'not converted to json: %s' % (obj.__class__.__name__)
            print msg
            # return {} # convert un-json-able object to empty object
            return msg # substitute object with msg

class linenum():
    import os, sys

    def __init__(self, newline=True):
        self.newline = newline

    def __repr__(self):
        try:
            raise Exception
        except:
            frame = sys.exc_info()[2].tb_frame.f_back
            return '%s:%s:%s%s'%(
                os.path.basename(frame.f_code.co_filename), 
                frame.f_code.co_name, 
                frame.f_lineno, 
                '\n' if self.newline else ''
            )

def wktsql(polylist):
    wkts = ['ST_GeomFromText(\'%s\',4326)'%(i) for i in polylist]
    return 'ST_Union(ARRAY[%s])'%(','.join(wkts)) if wkts else ''
    