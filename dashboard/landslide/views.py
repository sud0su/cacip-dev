from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Avg, Count, Sum, Q, F, Func
from django.db import connection, connections
from django.utils.translation import ugettext as _

from .enumerations import DASHBOARD_META
from geonode.utilscustom import set_query_parameter, dict_ext, list_ext, JSONEncoderCustom, include_section, RawSQL_nogroupby, query_to_dicts
from .models import MegacampLandslideRisk
from dashboard.baseline.models import BgdCampShelterfootprintUnosatReachV1Jan, CxbHealthFacilities

import urllib
import requests

def get_dashboard_meta():
	return DASHBOARD_META

def get_landslide(request, areageom=None, areatype=None, areacode=None, includes=[], excludes=[], response=dict_ext()):

	query_landslide = MegacampLandslideRisk.objects.all()

	# landslide_grouped = query_landslide.\
	# 	annotate(
	# 		count_landslide=Count('pk'),
	# 	).\
	# 	extra(
	# 		select={
	# 			'cmp_name':'"BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan".cmp_name',
	# 			'count':'count("BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan".*)',
	# 		},
	# 		tables=['BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan'],
	# 		where=['ST_Intersects(megacamp_landslide_risk.geom_4326,"BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan".the_geom)'], 
	# 	).\
	# 	values('cmp_name','dn','count').\
	# 	order_by('cmp_name','dn')

	# print 'landslide_grouped\n', landslide_grouped.query

	sql_shelter = \
	'''
	SELECT 
		public."Camp_pop_03_2019"."Upazila" as upazila,
		public."Camp_pop_03_2019"."Union" as union,
		public."Camp_pop_03_2019"."New_Camp_N" as camp,
		public.megacamp_landslide_risk.dn as risk_level,
		COUNT(DISTINCT(public."BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan".fid)) as shelter_at_risk_count
	FROM 
		public.megacamp_landslide_risk,
		public."BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan" 
			JOIN public."Camp_pop_03_2019" 
			ON public."BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan".cmp_name = public."Camp_pop_03_2019"."New_Camp_N"
			JOIN public."T190310_Outline_RRC_Camp_A11" 
			ON public."Camp_pop_03_2019"."New_Camp_N" = public."T190310_Outline_RRC_Camp_A11"."New_Camp_N"
	WHERE 
		ST_Intersects(public.megacamp_landslide_risk.geom_4326, public."BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan".the_geom)
	GROUP BY 1, 2, 3, 4
	ORDER BY 1, 2, 3, 4	
	'''

	sql_hltfac = \
	'''
	SELECT 
		public."Camp_pop_03_2019"."New_Camp_N" as camp,
		public.megacamp_landslide_risk.dn as risk_level,
		COUNT(DISTINCT(public."cxb_health_facilities".fid)) as hltfac_at_risk_count
	FROM 
		public.megacamp_landslide_risk,
		public."cxb_health_facilities" 
			JOIN public."Camp_pop_03_2019" 
			ON public."cxb_health_facilities"."Camp_Name" = public."Camp_pop_03_2019"."New_Camp_N"
			JOIN public."T190310_Outline_RRC_Camp_A11" 
			ON public."Camp_pop_03_2019"."New_Camp_N" = public."T190310_Outline_RRC_Camp_A11"."New_Camp_N"
	WHERE 
		ST_Intersects(public.megacamp_landslide_risk.geom_4326, public."cxb_health_facilities".the_geom)
	GROUP BY 1, 2
	ORDER BY 1, 2	
	'''

	LANDSLIDE_LEVEL_CODES = [2, 3]
	LANDSLIDE_LEVEL_NAMES_SHORT = {
		# 1: 'low', 
		2: 'med', 
		3: 'high',
	}
	LANDSLIDE_LEVEL_NAMES_SHORT_ORDER = [LANDSLIDE_LEVEL_NAMES_SHORT[i] for i in LANDSLIDE_LEVEL_CODES]
	LANDSLIDE_LEVEL_NAMES_LONG = {
		# 'low': 'Low', 
		'med': 'Medium', 
		'high': 'High',
	}
	LANDSLIDE_LEVEL_NAMES_SHORT_ORDER_PLUS_NOT_ATRISK = LANDSLIDE_LEVEL_NAMES_SHORT_ORDER + ['not_at_risk']
	LANDSLIDE_LEVEL_NAMES_LONG_PLUS_NOT_ATRISK = dict_ext(LANDSLIDE_LEVEL_NAMES_LONG.copy()).updateget({'not_at_risk': 'Not at Risk'})

	query_shelter = BgdCampShelterfootprintUnosatReachV1Jan.objects.all()
	query_hltfac = CxbHealthFacilities.objects.all()

	total_shelters_per_camp = {camp['cmp_name']: camp for camp in query_shelter.values('cmp_name').annotate(total_shelter=Count('pk')).filter(area_class='Structure')}
	total_hltfac_per_camp = {camp['camp_name']: camp for camp in query_hltfac.values('camp_name').annotate(total_hltfac=Count('pk'))}

	landslide_hltfac_per_camp = dict_ext()
	with connections['datastore'].cursor() as cursor:
		for camp in query_to_dicts(cursor, sql_hltfac):
			landslide_hltfac_per_camp.path(camp['camp'])[camp['risk_level']] = {'hltfac_at_risk_count':camp['hltfac_at_risk_count']}

	with connections['datastore'].cursor() as cursor:
		landslides = [
			dict_ext(camp).updateget({
				'risk_name': LANDSLIDE_LEVEL_NAMES_SHORT[camp['risk_level']],
				'shelter_count': total_shelters_per_camp[camp['camp']]['total_shelter'],
				'hltfac_count': total_hltfac_per_camp.get(camp['camp'], {}).get('total_hltfac') or 0,
				'hltfac_at_risk_count': landslide_hltfac_per_camp.pathget(camp['camp'], camp['risk_level'], 'hltfac_at_risk_count') or 0,
			})
			for camp in query_to_dicts(cursor, sql_shelter)
		]

	landslide = dict_ext({'child': dict_ext(), 'order': []})
	for camp in landslides:
		landslide['order'] += [camp.get('camp',''),] if camp.get('camp','') not in landslide['order'] else []
		row = landslide.path('child', camp.get('camp',''))
		row['camp'] = camp.get('camp','')
		row['union'] = camp.get('union','')
		row['upazila'] = camp.get('upazila','')
		row['shelter_'+camp.get('risk_name','').lower()] = camp.get('shelter_at_risk_count',0)
		row['hltfac_'+camp.get('risk_name','').lower()] = camp.get('hltfac_at_risk_count',0)
		row['hltfac_total'] = camp.get('hltfac_count',0)
		row['shelter_total'] = camp.get('shelter_count',0)
		row['shelter_at_risk'] = row.get('shelter_at_risk', 0) + camp.get('shelter_at_risk_count',0)
		row['hltfac_at_risk'] = row.get('hltfac_at_risk', 0) + camp.get('hltfac_at_risk_count',0)
		row['shelter_not_at_risk'] = row['shelter_total'] - row['shelter_at_risk']
		row['hltfac_not_at_risk'] = row['hltfac_total'] - row['hltfac_at_risk']

	landslide['column_keys'] = {
		'counts':[
			'camp',
			'union',
			'upazila',
		],
		'sums': [
			# 'shelter_low',
			'shelter_med',
			'shelter_high',
			# 'hltfac_low',
			'hltfac_med',
			'hltfac_high',
			'shelter_at_risk',
			'shelter_total',
			'hltfac_at_risk',
			'hltfac_total',		
		],
	}

	landslide['column_keys']['all'] = landslide['column_keys']['counts'] + landslide['column_keys']['sums']

	landslide['totals'] = dict_ext({
		key: len(set([i.get(key) for i in landslide['child'].values()])) 
		for key in landslide['column_keys']['counts']
	}).updateget({
		key: sum([i.get(key) or 0 for i in landslide['child'].values()])
		for key in landslide['column_keys']['sums']
	})

	landslide['totals'].updateget({
		'shelter_not_at_risk': landslide['totals']['shelter_total'] - landslide['totals']['shelter_at_risk'],
		'hltfac_not_at_risk': landslide['totals']['hltfac_total'] - landslide['totals']['hltfac_at_risk'],
	})

	# landslide['totals'] = {
	# 	'camp': len(set([i.get('camp') for i in landslide['child'].values()])),
	# 	'union': len(set([i.get('union') for i in landslide['child'].values()])),
	# 	'upazila': len(set([i.get('upazila') for i in landslide['child'].values()])),
	# 	'shelter_low': sum([i.get('shelter_low') or 0 for i in landslide['child'].values()]),
	# 	'shelter_med': sum([i.get('shelter_med') or 0 for i in landslide['child'].values()]),
	# 	'shelter_high': sum([i.get('shelter_high') or 0 for i in landslide['child'].values()]),
	# 	'hltfac_low': sum([i.get('hltfac_low') or 0 for i in landslide['child'].values()]),
	# 	'hltfac_med': sum([i.get('hltfac_med') or 0 for i in landslide['child'].values()]),
	# 	'hltfac_high': sum([i.get('hltfac_high') or 0 for i in landslide['child'].values()]),
	# 	'shelter_at_risk': sum([i.get('shelter_at_risk') or 0 for i in landslide['child'].values()]),
	# 	'shelter_total': sum([i.get('shelter_total') or 0 for i in landslide['child'].values()]),
	# 	'hltfac_at_risk': sum([i.get('hltfac_at_risk') or 0 for i in landslide['child'].values()]),
	# 	'hltfac_total': sum([i.get('hltfac_total') or 0 for i in landslide['child'].values()]),
	# }

	TABLE_SHELTER_HLTFAC_COLUMN_ORDER = [
		'camp',
		'union',
		'upazila',
		# 'shelter_low',
		'shelter_med',
		'shelter_high',
		# 'hltfac_low',
		'hltfac_med',
		'hltfac_high',
		# 'shelter_at_risk',
		'shelter_total',
		# 'hltfac_at_risk',
		'hltfac_total',	
	]

	response.updateget({
		'landslides': landslides,
		'total_shelters_per_camp': total_shelters_per_camp,
		'landslide_hltfac_per_camp': landslide_hltfac_per_camp,
		'landslide':landslide,
		'init_data': {
			'tables': {
				'table_shelter_hltfac': {
					'key': 'table_shelter_hltfac',
					'title': _('Shelter and Health Facilities in Landslide Risk Area'),
					'column_keys': landslide['column_keys']['all'],
					'parentdata': [landslide['totals'][i] for i in TABLE_SHELTER_HLTFAC_COLUMN_ORDER],
					# 'parentdata':[
					# 		len(set([i.get('camp') for i in landslide['child'].values()])),
					# 		len(set([i.get('union') for i in landslide['child'].values()])),
					# 		len(set([i.get('upazila') for i in landslide['child'].values()])),
					# 		sum([i.get('shelter_low') or 0 for i in landslide['child'].values()]),
					# 		sum([i.get('shelter_med') or 0 for i in landslide['child'].values()]),
					# 		sum([i.get('shelter_high') or 0 for i in landslide['child'].values()]),
					# 		sum([i.get('hltfac_low') or 0 for i in landslide['child'].values()]),
					# 		sum([i.get('hltfac_med') or 0 for i in landslide['child'].values()]),
					# 		sum([i.get('hltfac_high') or 0 for i in landslide['child'].values()]),
					# 		sum([i.get('shelter_at_risk') or 0 for i in landslide['child'].values()]),
					# 		sum([i.get('shelter_total') or 0 for i in landslide['child'].values()]),
					# 		sum([i.get('hltfac_at_risk') or 0 for i in landslide['child'].values()]),
					# 		sum([i.get('hltfac_total') or 0 for i in landslide['child'].values()]),
					# 	],
					'child':[{
						'values':[landslide.path('child',i,key) for key in TABLE_SHELTER_HLTFAC_COLUMN_ORDER],
						# 'values':[
						# 	landslide.path('child',i,'camp'),
						# 	landslide.path('child',i,'union'),
						# 	landslide.path('child',i,'upazila'),
						# 	landslide.path('child',i,'shelter_low') or 0,
						# 	landslide.path('child',i,'shelter_med') or 0,
						# 	landslide.path('child',i,'shelter_high') or 0,
						# 	landslide.path('child',i,'hltfac_low') or 0,
						# 	landslide.path('child',i,'hltfac_med') or 0,
						# 	landslide.path('child',i,'hltfac_high') or 0,
						# 	landslide.path('child',i,'shelter_at_risk') or 0,
						# 	landslide.path('child',i,'shelter_total') or 0,
						# 	landslide.path('child',i,'hltfac_at_risk') or 0,
						# 	landslide.path('child',i,'hltfac_total') or 0,
						# ],
						'code': urllib.quote(landslide.path('child',i,'camp'))				
					} for i in landslide['order']]
				}
			},
			'charts': {
				'chart_pie_hltfac': {
					'key': 'chart_pie_hltfac',
					'title': _('Health Facilities'),
					# 'labels': [LANDSLIDE_LEVEL_NAMES_LONG_PLUS_NOT_ATRISK[i] for i in LANDSLIDE_LEVEL_NAMES_SHORT_ORDER_PLUS_NOT_ATRISK],
					'values': [
						[LANDSLIDE_LEVEL_NAMES_LONG_PLUS_NOT_ATRISK[k], landslide['totals'].get('hltfac_'+k,0)] 
						for k in LANDSLIDE_LEVEL_NAMES_SHORT_ORDER_PLUS_NOT_ATRISK
					],
				},
				'chart_pie_shelter': {
					'key': 'chart_pie_shelter',
					'title': _('Shelters'),
					'labels': [LANDSLIDE_LEVEL_NAMES_LONG_PLUS_NOT_ATRISK[i] for i in LANDSLIDE_LEVEL_NAMES_SHORT_ORDER_PLUS_NOT_ATRISK],
					'values': [
						[LANDSLIDE_LEVEL_NAMES_LONG_PLUS_NOT_ATRISK[k], landslide['totals'].get('shelter_'+k,0)] 
						for k in LANDSLIDE_LEVEL_NAMES_SHORT_ORDER_PLUS_NOT_ATRISK
					],
					# 'values': [landslide['totals'].get('shelter_'+k,0) for k in LANDSLIDE_LEVEL_NAMES_SHORT_ORDER_PLUS_NOT_ATRISK],
				},
			}
		},
	})

	return response
