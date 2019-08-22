from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Avg, Count, Sum, Q
from django.utils.translation import ugettext as _

from geonode.utilscustom import set_query_parameter, dict_ext, list_ext, JSONEncoderCustom, include_section
from geonode.base.models import Region
from .models import CampPop032019, BgdCampShelterfootprintUnosatReachV1Jan, CxbHealthFacilities
from .enumerations import ADM_TYPES, DASHBOARD_META, ADM_FIELDS, AGE_GROUP_TYPES, AGE_GROUP_TYPES_KEYS

import urllib
import pandas as pd
import requests

def get_dashboard_meta():
	return DASHBOARD_META

# moved from geodb.views

def getBaselineInfoVillages(request):
	template = './baselineinfo.html'
	context_dict = {}
	# village = request.GET["v"]

	# context_dict = getCommonVillageData(village)

	# link = "https://www.ventusky.com/panel.php?link="+request.GET["x"]+";"+request.GET["y"]+"&lang=en-us&id="
	# f = urllib.urlopen(link)
	# myfile = f.read()
	headers = {'Cookie':{}}
	if 'parametr' in request.GET:
		response = requests.get("https://www.ventusky.com/aside/forecast.ajax.php?parametr="+request.GET["parametr"]+"&lon="+request.GET["lon"]+"&lat="+request.GET["lat"]+"&tz=Asia/Kabul&lang=en-ca", verify=False)
		return HttpResponse(response.content)
	else:
		response = requests.get("https://www.ventusky.com/panel.php?link="+request.GET["x"]+";"+request.GET["y"]+"&lang=en-ca&id=", verify=False)

	response.cookies = {}
	# print response.cookies
	context_dict['htmlrsult'] = response.content

	return render_to_response(template,
								  RequestContext(request, context_dict))

def get_adm_path(areacode):
	adm_path = []
	region = Region.objects.get(code=areacode)
	while region:
		adm_path += [{
			'level': region.level,
			'type': ADM_TYPES[region.level],
			'name': region.name,
			'code': region.code,
			'active': areacode == region.code,
			'child': [{
				'name': child_region.name,
				'code': child_region.code,
			} for child_region in Region.objects.filter(parent_id=region.id).order_by('name')],
		}]
		region = region.parent
	adm_path_reversed = adm_path[::-1]
	return adm_path_reversed

def get_adm_path_from_table_pop(areacode):
	adm_path = {}
	area_name = urllib.unquote(areacode)
	camps = CampPop032019.objects.filter(Q(district=area_name) | Q(upazila=area_name) | Q(union=area_name) | Q(new_camp_n=area_name))

	if not camps:
		return {}

	# for camp in camps:
	for idx, field in enumerate(ADM_FIELDS):
		checked_area_name = getattr(camps[0], field, '').strip()
		if checked_area_name:
			if idx not in adm_path:
				adm_path[idx] = {
					'name': checked_area_name,
					'code': urllib.quote(checked_area_name),
					'type': ADM_TYPES[idx],
					'level': idx,
					'field': ADM_FIELDS[idx],
					'active': area_name == checked_area_name,
					'sibling': [],
				}
				if adm_path[idx]['active']:
					break

	child_idx = idx + 1
	if child_idx in ADM_TYPES:
		adm_path[child_idx] = {
			'type': ADM_TYPES[child_idx],
			'level': child_idx,
			'field': ADM_FIELDS[child_idx],
			'active': False,
			'sibling': [],
		}

	for idx, p in adm_path.items():
		field = ADM_FIELDS[idx]
		camps = CampPop032019.objects.distinct(field).order_by(field)
		if idx > 0:
			parent_field = ADM_FIELDS[idx - 1]
			parent_name = adm_path[idx - 1]['name']
			camps = camps.filter(**{parent_field:parent_name})
		for camp in camps:
			checked_area_name = getattr(camp, field, '').strip()
			adm_path[idx]['sibling'] += [{
				'name': checked_area_name,
				'code': urllib.quote(checked_area_name),
			}]

		# # child
		# if idx < len(ADM_TYPES):
		# 	child_field = ADM_FIELDS[idx+1]
		# 	camps = CampPop032019.objects.filter(**{field:p['name']}).distinct(child_field).order_by(child_field)
		# 	for camp in camps:
		# 		checked_area_name = getattr(camps[0], child_field, '').strip()
		# 		adm_path[idx]['child'] += [{
		# 			'name': checked_area_name,
		# 			'code': urllib.quote(checked_area_name),
		# 		}]

	return adm_path

def get_areatype_from_areacode(areacode):
	region = Region.objects.get(code=areacode)
	areatype = ADM_TYPES[region.level]
	return areatype

def get_camps_from_parents(parentcodes, admlevel):
	# camp_level = 3
	area = CampPop032019.objects.filter(**{ADM_FIELDS[admlevel]+'__in':parentcodes})
	# for i in range(admlevel, camp_level):
	# 	area = CampPop032019.objects.filter(parent__in=area).order_by('name')
	return area

def get_baseline(request, areageom=None, areatype=None, areacode=None, includes=[], excludes=[], response=dict_ext()):

	# default areacode to 'Cox\'s Bazar' if none specified
	if not areacode and not areageom:
		areacode = 'Cox\'s Bazar'

	# base queries
	query_pop = CampPop032019.objects.all()
	query_shelter = BgdCampShelterfootprintUnosatReachV1Jan.objects.all()
	query_hltfac = CxbHealthFacilities.objects.all()
	
	# for breadcrumb
	adm_path = get_adm_path_from_table_pop(areacode) 

	# current selected area
	active_adm = [adm for adm in adm_path.values() if adm.get('active')][0]

	# child of current selected area
	child_level = active_adm['level'] + 1
	child_adm = adm_path[child_level] if child_level in ADM_TYPES else active_adm

	HLTFAC_TYPES = list(query_hltfac.values_list('facility_t', flat=True).order_by('facility_t').distinct('facility_t').\
		exclude(facility_t__isnull=True).exclude(facility_t__exact=''))

	# cached = active_adm['type'] in ADM_TYPES.values()

	# # get camps using union, upazila, district
	# areatype_mappings = {
	# 	's[0]':'ssid',
	# 	'union':'union',
	# 	'upazila':'upazila',
	# 	'district':'district',
	# }
	# if areatype in areatype_mappings:
	# 	if areatype in ['camp']:
	# 		query_pop = query_pop.filter(**{areatype_mappings[areatype]:areacode})
	# 	else:
	# 		query_pop = query_pop.filter(**{areatype_mappings[areatype]:active_adm['name']})

	# get camp names using get_camps_from_parents(), use camp names to filter query
	camp_ids = filter(None, [r.new_camp_n for r in get_camps_from_parents([active_adm['name']], active_adm['level'])]) 
	query_pop = query_pop.filter(new_camp_n__in=camp_ids)
	query_shelter = query_shelter.filter(cmp_name__in=camp_ids, area_class='Structure')
	query_hltfac = query_hltfac.filter(camp_name__in=camp_ids)

	# prepare db field names for query, using mapping as alias for better descriptive names
	age_groups_fields_mappings = {
		'infant':{
			'female':'infant_fem',
			'male':'infant_mal',
		},
		'1_4':{
			'female':'field_1_4_child',
			'male':'field_1_4_chil_field',
		},
		'5_11':{
			'female':'field_5_11_chil',
			'male':'field_5_11_chi_field',
		},
		'12_17':{
			'female':'field_12_17_chi',
			'male':'field_12_17_ch_field',
		},
		'18_59':{
			'female':'field_18_59_adu',
			'male':'field_18_59_ad_field',
		},
		'60':{
			'female':'field_60_elderl',
			'male':'field_60_elde_1',
		},
	}
	age_groups_fields = [f for k, age in age_groups_fields_mappings.items() for f in age.values()]
	agg_fields = [
		'area_sqm',
		'area_acre',
		'shape_leng',
		'shape_area',
		'id',
		'total_fami',
		'total_indi',
		'containhh',		
	]

	# prepare aggregate/annotate function in a dict
	agg_func_dict = {f:Sum(f) for f in agg_fields + age_groups_fields}

	# aggregate/annotate query using dict converted to keyword arguments as parameters
	agg_pop = query_pop.aggregate(**agg_func_dict)
	annotate_pop = query_pop.values(child_adm['field']).annotate(**agg_func_dict)
	annotate_shelter = query_shelter.values('cmp_name').annotate(shelter_count=Count('pk'),shelter_area_m2=Sum('area_m2'))
	annotate_hltfac = query_hltfac.values('camp_name','facility_t').annotate(hltfac_count=Count('pk'))

	# create panda dataframe from pop, the adm data will be used for grouping
	df_pop = pd.DataFrame.from_records(query_pop.values(*ADM_FIELDS),index='new_camp_n')

	# join shelter to pop then group by adm
	df_annotate_shelter = pd.DataFrame.from_records(annotate_shelter,index='cmp_name')
	df_annotate_shelter_pop = df_annotate_shelter.join(df_pop)
	df_annotate_shelter_pop_groupby = df_annotate_shelter_pop.groupby([child_adm['field']]).sum() \
		if child_adm['field'] in df_annotate_shelter_pop.keys() \
		else df_annotate_shelter_pop
	# df_annotate_shelter_pop_groupby = df_annotate_shelter_pop_groupby.sum()

	# join hltfac to pop then group by adm
	df_annotate_hltfac = pd.DataFrame.from_records(annotate_hltfac,index='camp_name')
	df_annotate_hltfac_pop = df_annotate_hltfac.join(df_pop)
	df_annotate_hltfac_pop_groupby = df_annotate_hltfac_pop.groupby([child_adm['field'],'facility_t']) \
		if child_adm['field'] in df_annotate_hltfac_pop.keys() \
		else df_annotate_hltfac_pop.groupby(['facility_t'])
	df_annotate_hltfac_pop_groupby = df_annotate_hltfac_pop_groupby.sum()

	# generic formatter
	response.updateget({
		f:agg_pop.get(f, '') for f in agg_fields
	}).updateget({
		'adm_path': adm_path,
		'area_code': active_adm['code'],
		'area_type': active_adm['type'],
		'area_name': active_adm['name'],
		'area_level': active_adm['level'],
		'is_bottom_level': active_adm['level'] == len(ADM_TYPES)-1,
		'pop_by_age_group': {k:{k2:agg_pop.get(v2,0) for k2,v2 in v.items()} for k,v in age_groups_fields_mappings.items()},
		'child_area_type': child_adm['type'],
		'child_area_level': child_adm['level'],
		'hltfac_types': HLTFAC_TYPES,
		'hltfac_count': df_annotate_hltfac_pop_groupby['hltfac_count'].sum(),
		'shelter_count': df_annotate_shelter_pop_groupby['shelter_count'].sum(),
		'shelter_area_m2': df_annotate_shelter_pop_groupby['shelter_area_m2'].sum(),
		'hltfac_count_by_type': dict(df_annotate_hltfac_pop.groupby(['facility_t']).sum()['hltfac_count']),
		'child': [
			dict_ext({
				f:ann.get(f, '') for f in agg_fields
			}).updateget({
				'area_code': urllib.quote(ann[child_adm['field']]),
				'area_type': child_adm['type'],
				'area_name': ann[child_adm['field']],
				'pop_by_age_group': {k:{k2:ann.get(v2,0) for k2,v2 in v.items()} for k,v in age_groups_fields_mappings.items()},
				'hltfac_count': sum(df_annotate_hltfac_pop_groupby['hltfac_count'].get(ann[child_adm['field']], [])),
				'hltfac_count_by_type': dict(df_annotate_hltfac_pop_groupby['hltfac_count'].get(ann[child_adm['field']], {})),
				'shelter_count': df_annotate_shelter_pop_groupby['shelter_count'].get(ann[child_adm['field']]),
				'shelter_area_m2': df_annotate_shelter_pop_groupby['shelter_area_m2'].get(ann[child_adm['field']]),
			}) for ann in annotate_pop
		],
		# 'annotate_hltfac': annotate_hltfac,
	})
	
	# specific formatter
	response.updateget({
		'init_data': {
			'charts': {
				'chart_pop_by_age_group': {
					'key': 'chart_pop_by_age_group',
					'title': _('Population'),
					'labels_y': [AGE_GROUP_TYPES[k] for k in AGE_GROUP_TYPES_KEYS],
					'data': {
						'male': [-response['pop_by_age_group'][k]['male'] for k in AGE_GROUP_TYPES_KEYS],
						'female': [response['pop_by_age_group'][k]['female'] for k in AGE_GROUP_TYPES_KEYS],
					}
				},
				'chart_hltfac': {
					'key': 'chart_hltfac',
					'title': _('Health Facilities'),
					'labels': HLTFAC_TYPES,
					'values': [response['hltfac_count_by_type'].get(k,0) for k in HLTFAC_TYPES],
				},
				'chart_pop_by_child_adm': {
					'key': 'chart_pop_by_child_adm',
					'title': _('Population'),
					'labels': [v['area_name'] for v in response['child']],
					'values': [v['total_indi'] for v in response['child']],
				},
				'chart_shelter_by_child_adm': {
					'key': 'chart_shelter_by_child_adm',
					'title': _('Shelter'),
					'labels': [v['area_name'] for v in response['child']],
					'values': [v['shelter_count'] for v in response['child']],
				},
			},
			'tables': {
				'table_pop_shelter': {
					'key': 'table_pop_shelter',
					'title': _('Overview of Population'),
					'parentdata':[
							response['area_name'],
							response['total_indi'],
							response['total_fami'],
							response['containhh'],
							response['shelter_count'],
						],
					'child':[{
						'values':[
							v['area_name'],
							v['total_indi'],
							v['total_fami'],
							v['containhh'],
							v['shelter_count'],
						],
						'code': v['area_code'],
					} for v in response['child']],
				},
				'table_hltfac': {
					'key': 'table_hltfac',
					'title': _('Health Facilities'),
					'parentdata': \
						[response['area_name']]+\
						[response['hltfac_count_by_type'].get(k,0) for k in HLTFAC_TYPES]+\
						[sum(response['hltfac_count_by_type'].values())],
					'child': [{
						'values': \
							[v['area_name']]+\
							[v['hltfac_count_by_type'].get(k,0) for k in HLTFAC_TYPES]+\
							[sum(v['hltfac_count_by_type'].values())],
						'code': v['area_code'],
					} for v in response['child']],
				},
			},
		}
	})

	return response