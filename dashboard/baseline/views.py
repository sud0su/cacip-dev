from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Avg, Count, Sum, Q

from geonode.utilscustom import set_query_parameter, dict_ext, list_ext, JSONEncoderCustom, include_section
from geonode.base.models import Region
from .models import CampPop032019
from .enumerations import ADM_TYPES, DASHBOARD_META

import urllib
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

	adm_fields = ['district', 'upazila', 'union', 'new_camp_n']

	# for camp in camps:
	for idx, field in enumerate(adm_fields):
		checked_area_name = getattr(camps[0], field, '').strip()
		if area_name:
			if idx not in adm_path:
				adm_path[idx] = {}
				adm_path[idx]['name'] = checked_area_name
				adm_path[idx]['code'] = urllib.quote_plus(checked_area_name)
				adm_path[idx]['type'] = ADM_TYPES[idx]
				adm_path[idx]['level'] = idx
				adm_path[idx]['active'] = area_name == checked_area_name
				adm_path[idx]['sibling'] = []
				if adm_path[idx]['active']:
					break

	for idx, p in adm_path.items():
		field = adm_fields[idx]
		camps = CampPop032019.objects.distinct(field).order_by(field)
		for camp in camps:
			checked_area_name = getattr(camps[0], field, '').strip()
			adm_path[idx]['sibling'] += [{
				'name': checked_area_name,
				'code': urllib.quote_plus(checked_area_name),
			}]

	return adm_path

def get_areatype_from_areacode(areacode):
	region = Region.objects.get(code=areacode)
	areatype = ADM_TYPES[region.level]
	return areatype

def get_child_from_parents(parentcodes, admlevel):
	# camp_level = 3
	adm_fields = ['district', 'upazila', 'union', 'new_camp_n']
	area = CampPop032019.objects.filter(**{adm_fields[admlevel]+'__in':parentcodes})
	# for i in range(admlevel, camp_level):
	# 	area = CampPop032019.objects.filter(parent__in=area).order_by('name')
	return area

def get_baseline(request, areageom=None, areatype=None, areacode=None, includes=[], excludes=[], response=dict_ext()):

	if not areacode and not areageom:
		return {}

	query_camps_pop = CampPop032019.objects.all()
	adm_path = get_adm_path_from_table_pop(areacode) # for breadcrumb
	current_region = adm_path[len(adm_path)-1]

	# cached = current_region['type'] in ADM_TYPES.values()

	# # get camps using union, upazila, district
	# areatype_mappings = {
	# 	's[0]':'ssid',
	# 	'union':'union',
	# 	'upazila':'upazila',
	# 	'district':'district',
	# }
	# if areatype in areatype_mappings:
	# 	if areatype in ['camp']:
	# 		query_camps_pop = query_camps_pop.filter(**{areatype_mappings[areatype]:areacode})
	# 	else:
	# 		query_camps_pop = query_camps_pop.filter(**{areatype_mappings[areatype]:current_region['name']})

	# get camps using get_child_from_parents()
	admlevel = dict_ext(ADM_TYPES).getkeyfromvalue(current_region['type'])
	camp_ids = filter(None, [r.new_camp_n for r in get_child_from_parents([current_region['name']], admlevel)]) 
	query_camps_pop = query_camps_pop.filter(new_camp_n__in=camp_ids)

	age_groups_fields_mappings = {
		'infant':{
			'male':'infant_fem',
			'female':'infant_mal',
		},
		'1_4':{
			'male':'field_1_4_child',
			'female':'field_1_4_chil_field',
		},
		'5_11':{
			'male':'field_5_11_chil',
			'female':'field_5_11_chi_field',
		},
		'12_17':{
			'male':'field_12_17_chi',
			'female':'field_12_17_ch_field',
		},
		'18_59':{
			'male':'field_18_59_adu',
			'female':'field_18_59_ad_field',
		},
		'60':{
			'male':'field_60_elderl',
			'female':'field_60_elde_1',
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
	agg_pop = query_camps_pop.aggregate(**{f:Sum(f) for f in agg_fields + age_groups_fields})

	# generic formatter
	response.update({f:agg_pop.get(f, '') for f in agg_fields})
	response.update({
		'pop_by_age_group': {k:{k2:agg_pop.get(v2,0) for k2,v2 in v.items()} for k,v in age_groups_fields_mappings.items()},
		'adm_path': adm_path,
		'area_code': areacode,
		'area_type': areatype,
		'area_name': current_region['name'],
	})

	return response