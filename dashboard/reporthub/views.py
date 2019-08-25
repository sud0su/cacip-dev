from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Avg, Count, Sum, Q, F, Func
from django.db.models.expressions import RawSQL
from django.utils.translation import ugettext as _

from geonode.utilscustom import set_query_parameter, dict_ext, list_ext, JSONEncoderCustom, include_section, RawSQL_nogroupby
from geonode.base.models import Region
from .models import TempBeneficiaries
from .enumerations import DASHBOARD_META, ADM_CODE_FIELDS, ADM_NAME_FIELDS, ADM_TYPES, FILTER_CODE_FIELDS, FILTER_NAME_FIELDS

import urllib
import pandas as pd
import requests
import functools
import re
import operator, functools

def get_dashboard_meta():
	return DASHBOARD_META

def get_adm_path_from_table_beneficiaries(areacode):
	adm_path = {}
	area_name = urllib.unquote(areacode)

	# convert areacode to integer
	try:
		areacode_int = int(areacode)
	except:
		areacode_int = None

	camps = TempBeneficiaries.objects.\
		filter(Q(admin0pcode=areacode) | Q(admin1pcode=areacode_int) | Q(admin2pcode=areacode_int) | Q(admin3pcode=areacode) | Q(admin4pcode=areacode)).\
		values(*(ADM_CODE_FIELDS + ADM_NAME_FIELDS.values()))[:1]

	if not camps:
		return {}

	# for camp in camps:
	for field_code in ADM_CODE_FIELDS:
		field_name = ADM_NAME_FIELDS[field_code]
		checked_area_code = camps[0].get(field_code, '')
		level = ADM_CODE_FIELDS.index(field_code)
		if checked_area_code:
			if level not in adm_path:
				adm_path[level] = {
					'name': camps[0].get(field_name, ''),
					'code': checked_area_code,
					'type': ADM_TYPES[level],
					'level': level,
					'field': field_code,
					'active': (areacode == checked_area_code) or (areacode_int == checked_area_code),
					'sibling': [],
				}
				if adm_path[level]['active']:
					break

	# add child adm to adm_path
	child_level = level + 1
	if child_level in ADM_TYPES:
		adm_path[child_level] = {
			'type': ADM_TYPES[child_level],
			'level': child_level,
			'field': ADM_CODE_FIELDS[child_level],
			'active': False,
			'sibling': [],
		}

	# populate siblings
	for level, adm in adm_path.items():
		field_code = ADM_CODE_FIELDS[level]
		field_name = ADM_NAME_FIELDS[field_code]
		camps = TempBeneficiaries.objects.values(field_code, field_name).order_by(field_code, field_name).distinct(field_code, field_name).\
			exclude(**{field_code+'__isnull':True})
		# print 'camps.query\n', camps.query
		if level > 0:
			parent_level = level - 1
			parent_field_code = ADM_CODE_FIELDS[parent_level]
			camps = camps.filter(**{parent_field_code:adm_path[parent_level]['code']})
		for camp in camps:
			adm_path[level]['sibling'] += [{
				'name': camp.get(field_name, ''),
				'code': camp.get(field_code, ''),
			}]

	return adm_path

def get_filter_path_from_table_beneficiaries(filters, FILTER_CODE_FIELDS_SELECTED):

	if not filters:
		return {}

	filter_path = {}
	# area_name = urllib.unquote(areacode)

	# convert areacode to integer
	# try:
	# 	areacode_int = int(areacode)
	# except:
	# 	areacode_int = None
	FILTER_NAME_FIELDS_SELECTED = dict_ext(FILTER_NAME_FIELDS).within(*FILTER_CODE_FIELDS_SELECTED)

	camps = TempBeneficiaries.objects.\
		filter(**filters).\
		values(*(FILTER_CODE_FIELDS_SELECTED + FILTER_NAME_FIELDS_SELECTED.values()))[:1]

	if not camps:
		return {}

	# for camp in camps:
	for field_code in filters.keys():
		field_name = FILTER_NAME_FIELDS_SELECTED[field_code]
		field_code_value = camps[0].get(field_code, '')
		level = FILTER_CODE_FIELDS_SELECTED.index(field_code)
		if field_code_value:
			if level not in filter_path:
				filter_path[level] = {
					'name': camps[0].get(field_name, ''),
					'code': urllib.quote(field_code_value),
					'type': field_code,
					'level': level,
					'field': field_code,
					'active': False,
					'sibling': [],
				}
				# if filter_path[level]['active']:
				# 	break
	filter_path[len(filter_path)-1]['active'] = True

	# add child adm to filter_path
	child_level = len(filter_path)
	if child_level <= len(FILTER_CODE_FIELDS_SELECTED):
		filter_path[child_level] = {
			'type': FILTER_CODE_FIELDS_SELECTED[child_level],
			'level': child_level,
			'field': FILTER_CODE_FIELDS_SELECTED[child_level],
			'active': False,
			'sibling': [],
		}

	# populate siblings
	for level, filter in filter_path.items():
		field_code = FILTER_CODE_FIELDS_SELECTED[level]
		field_name = FILTER_NAME_FIELDS_SELECTED[field_code]
		camps = TempBeneficiaries.objects.values(field_code, field_name).order_by(field_code, field_name).distinct(field_code, field_name).\
			exclude(**{field_code+'__isnull':True})
		# print 'camps.query\n', camps.query
		if level > 0:
			filters_ancestor = {k:v for k,v in filters.items() if FILTER_CODE_FIELDS_SELECTED.index(k) < level}
			camps = camps.filter(**filters_ancestor)
		for camp in camps:
			filter_path[level]['sibling'] += [{
				'name': camp.get(field_name, ''),
				'code': urllib.quote(camp.get(field_code, '')),
			}]

	return filter_path

def get_reporthub(request, areageom=None, areatype=None, areacode=None, includes=[], excludes=[], response=dict_ext()):

	# default areacode to 'CB' if none specified
	if not areacode and not areageom:
		areacode = 'CB'

	# for breadcrumb
	adm_path = get_adm_path_from_table_beneficiaries(areacode) 

	# base queries
	query_beneficiaries = TempBeneficiaries.objects.all()
	FILTER_OPTIONAL_FIELDS = ['donor','organization','cluster_id','reporting_period']
	FILTER_OPTIONAL_FIELDS_EXC_REPORTING_PERIOD = list_ext(FILTER_OPTIONAL_FIELDS).without('reporting_period')
	FILTER_OPTIONAL_FIELDS_NAME = {
		'donor': 'donor',
		'organization': 'organization',
		'cluster_id': 'cluster',
		'reporting_period': 'reporting_period',
	}

	beneficiaries_adm_filters = {adm['field']:urllib.unquote(adm['code']) if type(adm['code']) not in [int, long] else adm['code'] for idx, adm in adm_path.items() if 'code' in adm}
	beneficiaries_filters = beneficiaries_adm_filters.copy()
	beneficiaries_filters.update({f+'__in':filter(None,request.GET.get(f,'').split(',')) for f in FILTER_OPTIONAL_FIELDS_EXC_REPORTING_PERIOD if f in request.GET})
	if 'reporting_period' in request.GET:
		start, end = request.GET['reporting_period'].split(',')
		beneficiaries_filters.update({'reporting_period__gte':start,'reporting_period__lte':end})
		# beneficiaries_filters.update({'reporting_period__range':[start,end]})
	# fact=functools.reduce(mult, filter(None,request.GET.get(f,'').split(',')))
	# print 'beneficiaries_filters', beneficiaries_filters
	beneficiaries_adm_filtered = query_beneficiaries.filter(**beneficiaries_adm_filters)
	beneficiaries_filtered = query_beneficiaries.filter(**beneficiaries_filters)
	# print beneficiaries_filtered.query

	beneficiaries_annotated = beneficiaries_filtered.\
		values('cluster','activity_description_name','indicator_id','indicator_name').\
		annotate(
			population=Sum('total'),
			population_male=Sum('boys')+Sum('men')+Sum('elderly_men'),
			population_female=Sum('girls')+Sum('women')+Sum('elderly_women'),
			# unit_type_names=Func(Func(F('unit_type_name'), function='DISTINCT'), function='STRING_AGG'),
			units=Sum('units'),
			unit_type_names=RawSQL_nogroupby("STRING_AGG(DISTINCT(unit_type_name), ', ')",()),
			unit_type_donors=RawSQL_nogroupby("STRING_AGG(DISTINCT(donor), ', ')",()),
			unit_type_organizations=RawSQL_nogroupby("STRING_AGG(DISTINCT(organization), ', ')",()),
		).\
		exclude(indicator_name__isnull=True)
	# print beneficiaries_annotated.query
	

	beneficiaries_units = beneficiaries_filtered.\
		values('unit_type_id','unit_type_name').\
		annotate(
			units=Sum('units'),
		).\
		exclude(indicator_name__isnull=True).\
		exclude(units=0).\
		exclude(unit_type_id__isnull=True)

	# print beneficiaries_units.query
	
	# FILTER_CODE_FIELDS_SELECTED = filter(None, request.GET.get('filter_codes','').split(',')) or FILTER_CODE_FIELDS
	# filters = {f: request.GET[f] for f in FILTER_CODE_FIELDS_SELECTED if f in request.GET}
	# filter_path = get_filter_path_from_table_beneficiaries(filters, FILTER_CODE_FIELDS_SELECTED) 

	# query_activities = query_beneficiaries.values('cluster','activity_description_name').annotate(project_count=Count('index'))

	replace_list = ['# of ', '# ']
	response.updateget({
		'adm_path': adm_path,
		# 'filter_path': filter_path,
		'filters': {
			f:{
				'key':f,
				'selected': filter(None,request.GET.get(f,'').split(',')), 
				'options':[{
					'key': urllib.quote(f2[f]),
					'value': f2[FILTER_OPTIONAL_FIELDS_NAME[f]],
				} for f2 in beneficiaries_adm_filtered.values(f,FILTER_OPTIONAL_FIELDS_NAME[f]).order_by(f).distinct(f).exclude(**{f+'__isnull':True})],
			}
		for f in FILTER_OPTIONAL_FIELDS},
		'areacode': areacode,
		'beneficiaries_annotated': beneficiaries_annotated,
		'init_data': {
			'table': {
				'table_benficiaries': {
					'child': [{
						'values': [
							i['activity_description_name'],
							i['indicator_name'],
							i['cluster'],
							i['units'],
							i['population'],
							i['unit_type_names'],
							i['unit_type_donors'],
							i['unit_type_organizations'],
						],
						'code': i['activity_description_name'],

					} for i in beneficiaries_annotated],
					'columns': [
						_('Activity Description Name'),
						_('Indicator Name'),
						_('Cluster'),
						_('Units'),
						_('Population'),
						_('Unit Type Names'),
						_('Unit Type Donors'),
						_('Unit Type Organizations'),
					]
				}
			},
			'total': [{	
				'key': i['unit_type_id'],
				'value': i['units'],
				'name': functools.reduce(lambda x,y:  (x or '').replace(y,''), replace_list, i['unit_type_name']),
			} for i in beneficiaries_units.order_by('-units')[:10]],
		}
	})

	return response
