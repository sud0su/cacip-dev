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
from .enumerations import (DASHBOARD_META, ADM_CODE_FIELDS, ADM_NAME_FIELDS, ADM_TYPES, FILTER_CODE_FIELDS, FILTER_NAME_FIELDS,
	FILTER_OPTIONAL_FIELDS, FILTER_OPTIONAL_FIELDS_NAME)

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
			if level == 4:
				camps = camps.filter(admin4pcode__startswith=adm_path[parent_level]['code'])
			else:
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

def get_beneficiaries_optional_filtered(beneficiaries_base_filtered, field):
	beneficiaries_optional_filtered = beneficiaries_base_filtered.values(field,FILTER_OPTIONAL_FIELDS_NAME[field]).order_by(field).distinct(field).exclude(**{field+'__isnull':True})
	print beneficiaries_optional_filtered.query
	if field == 'donor':
		donors = set()
		for row in beneficiaries_optional_filtered:
			donors.update(map(lambda s: s.strip(), row[field].split(',')))
		beneficiaries_optional_filtered = [{field:d} for d in sorted(donors)]
	return beneficiaries_optional_filtered

def get_reporthub(request, areageom=None, areatype=None, areacode=None, includes=[], excludes=[], response=dict_ext(), **kwargs):

	# default areacode to 'CB' if none specified
	if not areacode and not areageom:
		areacode = 'CB'

	FILTER_OPTIONAL_FIELDS_EXC_REPORTING_PERIOD_EXC_DONOR = list_ext(FILTER_OPTIONAL_FIELDS).without(['reporting_period','donor'])

	# for breadcrumb
	adm_path = get_adm_path_from_table_beneficiaries(areacode) 

	# current selected area
	active_adm = [adm for adm in adm_path.values() if adm.get('active')][0]

	# child of current selected area
	child_level = active_adm['level'] + 1
	child_adm = adm_path[child_level] if child_level in ADM_TYPES else active_adm

	# base queries
	query_beneficiaries = TempBeneficiaries.objects.all()

	if active_adm['type'] == 'camp':
		beneficiaries_adm_filters = {'admin4pcode__startswith':active_adm['code']}
	else:
		beneficiaries_adm_filters = {adm['field']:urllib.unquote(adm['code']) if type(adm['code']) not in [int, long] else adm['code'] for idx, adm in adm_path.items() if 'code' in adm}
	beneficiaries_filters = beneficiaries_adm_filters.copy()
	beneficiaries_base_filtered = query_beneficiaries.filter(**beneficiaries_adm_filters)
	if request.GET.get('page'):
		cluster_id = list_ext(DASHBOARD_META['pages']).findchilddict('name', request.GET['page']).get('cluster_id')
		if cluster_id:
			beneficiaries_filters.update({'cluster_id': cluster_id})
			beneficiaries_base_filtered = beneficiaries_base_filtered.filter(**{'cluster_id': cluster_id})
			response.update({'cluster_id': cluster_id})
			cluster_list = list_ext(get_beneficiaries_optional_filtered(beneficiaries_base_filtered, 'cluster_id'))
			cluster_name = cluster_list.findchilddict('cluster_id', cluster_id).get(FILTER_OPTIONAL_FIELDS_NAME['cluster_id'])
			# cluster_name = [i for i in get_beneficiaries_optional_filtered(beneficiaries_base_filtered, 'cluster_id') if i['cluster_id'] == cluster_id]
			# response.update({'cluster': cluster_name[0].get(FILTER_OPTIONAL_FIELDS_NAME['cluster_id']) if cluster_name else None})
			response.update({'cluster': cluster_name})
	beneficiaries_filters.update({f+'__in':filter(None,request.GET.get(f,'').split(',')) for f in FILTER_OPTIONAL_FIELDS_EXC_REPORTING_PERIOD_EXC_DONOR if f in request.GET})
	if 'reporting_period' in request.GET:
		start, end = request.GET['reporting_period'].split(',')
		beneficiaries_filters.update({'reporting_period__gte':start,'reporting_period__lte':end})
		# beneficiaries_filters.update({'reporting_period__range':[start,end]})
	# fact=functools.reduce(mult, filter(None,request.GET.get(f,'').split(',')))
	# print 'beneficiaries_filters', beneficiaries_filters
	beneficiaries_filtered = query_beneficiaries.filter(**beneficiaries_filters)
	if 'donor' in request.GET:
		donors = filter(None, request.GET['donor'].split(','))
		if donors:
			donors_filter = functools.reduce(lambda x, y: x | y, [Q(donor__contains=d)for d in donors])
			beneficiaries_filtered = beneficiaries_filtered.filter(donors_filter)
	# print beneficiaries_filtered.query

	beneficiaries_annotated = beneficiaries_filtered.\
		values('cluster','activity_description_name','indicator_id','indicator_name','unit_type_id','unit_type_name').\
		annotate(
			population=Sum('total'),
			population_male=Sum('boys')+Sum('men')+Sum('elderly_men'),
			population_female=Sum('girls')+Sum('women')+Sum('elderly_women'),
			# unit_type_names=Func(Func(F('unit_type_name'), function='DISTINCT'), function='STRING_AGG'),
			units=Sum('units'),
			reporting_period=RawSQL_nogroupby("STRING_AGG(DISTINCT(SUBSTRING(reporting_period FROM 1 FOR 7)), ', ')",()),
			# unit_type_names=RawSQL_nogroupby("STRING_AGG(DISTINCT(unit_type_name), ', ')",()),
			donor=RawSQL_nogroupby("STRING_AGG(DISTINCT(donor), ', ')",()),
			organization=RawSQL_nogroupby("STRING_AGG(DISTINCT(organization), ', ')",()),
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
				} for f2 in get_beneficiaries_optional_filtered(beneficiaries_base_filtered, f)],
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
							i['unit_type_name'],
							i['donor'],
							i['organization'],
							i['reporting_period'],
						],
						'code': urllib.quote(i['activity_description_name']),
					} for i in beneficiaries_annotated],
					'columns': [
						_('Activity Description Name'),
						_('Indicator Name'),
						_('Cluster'),
						_('Units'),
						_('Population'),
						_('Unit Type Name'),
						_('Donors'),
						_('Organizations'),
						_('Reporting Period'),
					]
				}
			},
			'total': [{	
				'key': i['unit_type_id'],
				'value': i['units'],
				'name': functools.reduce(lambda x,y:  (x or '').replace(y,''), replace_list, i['unit_type_name']),
			} for i in beneficiaries_units.order_by('-units')],
		}
	})

	return response
