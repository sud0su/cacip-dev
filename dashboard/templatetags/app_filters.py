import json
import urllib
from urlparse import urlparse, urlunparse
from django import template
from django.core.serializers import serialize
from django.db.models.query import QuerySet, ValuesListQuerySet
from django.http import QueryDict
from geonode.utils import JSONEncoderCustom

register = template.Library()

@register.simple_tag
def readable(val):
    if val>=1000 and val<1000000:
    	# c = '{:.1f}'.format(val/1000).rstrip('0').rstrip('.') the last one
    	# print c
    	c = ('%.1f' % (round((val/1000), 2))).rstrip('0').rstrip('.')
    	# print c
    	return '{} K'.format(c) 
    	# b = '%.1f K' % (round((val/1000), 2))
    	# print b
    	# return ('%.1f K' % (round((val/1000), 2)))
    elif val>=1000000 and val<1000000000:
    	# c = '{:.1f}'.format(val/1000000).rstrip('0').rstrip('.')
    	# print c
    	b = ('%.1f' % (round((val/1000000), 2))).rstrip('0').rstrip('.')
    	return '{} M'.format(b)
    	# b = '%.1f M' % (round((val/1000000), 2))
    	# print b
    	# return ('%.1f M' % (round((val/1000000), 2)))
    else:
    	return ('%.1f' % round(val or 0)).rstrip('0').rstrip('.')

@register.filter( is_safe=True )
def jsonify(object):

    # if isinstance(object, ValuesListQuerySet):
    #     return json.dumps(list(object))
    # if isinstance(object, QuerySet):
    #     return serialize('json', object)
    # return json.dumps(object)
	return json.dumps(object,cls=JSONEncoderCustom)

@register.assignment_tag
def unjsonify(string):
	return json.loads(string)

@register.assignment_tag
def tolist(*args):
	return args

@register.assignment_tag
def tolistaddkey(*args):
	it = iter(args)
	zipit = zip(it, it)
	for key, val in zipit:
		val['key'] = key
	keys, vals = zip(*zipit)
	return vals

@register.filter
def listbykeys(object, keys):
	return [object.get(k.strip()) for k in keys.split(',')]

@register.filter
def createlist(object, listname):
	object[listname] = []
	return object[listname]

@register.filter
def listaddchild(object, listname):
	object[listname] = []
	return object[listname]

@register.simple_tag(takes_context=True)
def url_set_param(context, **kwargs):
    dict_ = context['request'].GET.copy()
    for field, value in kwargs.items():
		dict_[field] = value
    return dict_.urlencode()
