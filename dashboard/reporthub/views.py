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

def get_healthsector(request, areageom=None, areatype=None, areacode=None, includes=[], excludes=[], response=dict_ext()):

	# default areacode to 'CB' if none specified
	if not areacode and not areageom:
		areacode = 'CB'

	# base queries
	query_beneficiaries = TempBeneficiaries.objects.all()
	beneficiaries_annotated = query_beneficiaries.\
		values('cluster','activity_description_name','indicator_name').\
		annotate(
			population=Sum('total'),
			population_male=Sum('boys')+Sum('men')+Sum('elderly_men'),
			population_female=Sum('girls')+Sum('women')+Sum('elderly_women'),
			# unit_type_names=Func(Func(F('unit_type_name'), function='distinct'), function='string_agg'),
			units=Sum('units'),
			unit_type_names=RawSQL_nogroupby("string_agg(distinct(unit_type_name), ', ')",()),
		).\
		exclude(indicator_name__isnull=True)
	# print beneficiaries_annotated.query
	
	# for breadcrumb
	adm_path = get_adm_path_from_table_beneficiaries(areacode) 

	FILTER_CODE_FIELDS_SELECTED = filter(None, request.GET.get('filter_codes','').split(',')) or FILTER_CODE_FIELDS
	filters = {f: request.GET[f] for f in FILTER_CODE_FIELDS_SELECTED if f in request.GET}
	filter_path = get_filter_path_from_table_beneficiaries(filters, FILTER_CODE_FIELDS_SELECTED) 

	# query_activities = query_beneficiaries.values('cluster','activity_description_name').annotate(project_count=Count('index'))

	response.updateget({
		'adm_path': adm_path,
		'filter_path': filter_path,
		'areacode': areacode,
		'beneficiaries_annotated': beneficiaries_annotated,
	})

	return response
