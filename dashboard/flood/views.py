from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Avg, Count, Sum, Q, F, Func
from django.db import connection, connections
from django.utils.translation import ugettext as _

from .enumerations import DASHBOARD_META
from geonode.utilscustom import set_query_parameter, dict_ext, list_ext, JSONEncoderCustom, include_section, RawSQL_nogroupby, query_to_dicts, div_by_zero_is_zero, get_percent
from .models import MegacampFloodRisk
from dashboard.baseline.models import BgdCampShelterfootprintUnosatReachV1Jan, CxbHealthFacilities

import urllib
import requests

def get_dashboard_meta():
	return DASHBOARD_META

def get_floodrisk(request, areageom=None, areatype=None, areacode=None, includes=[], excludes=[], response=dict_ext()):

	query_floodrisk = MegacampFloodRisk.objects.all()

	# floodrisk_grouped = query_floodrisk.\
	# 	annotate(
	# 		count_floodrisk=Count('pk'),
	# 	).\
	# 	extra(
	# 		select={
	# 			'cmp_name':'"BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan".cmp_name',
	# 			'count':'count("BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan".*)',
	# 		},
	# 		tables=['BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan'],
	# 		where=['ST_Intersects(megacamp_flood_risk.geom_4326,"BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan".the_geom)'], 
	# 	).\
	# 	values('cmp_name','dn','count').\
	# 	order_by('cmp_name','dn')

	# print 'floodrisk_grouped\n', floodrisk_grouped.query

	# sql_shelter = \
	# '''
	# SELECT 
	# 	public."Camp_pop_03_2019"."Upazila" as upazila,
	# 	public."Camp_pop_03_2019"."Union" as union,
	# 	public."Camp_pop_03_2019"."New_Camp_N" as camp,
	# 	public.megacamp_flood_risk.dn as risk_level,
	# 	COUNT(DISTINCT(public."BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan".fid)) as shelter_at_risk_count
	# FROM 
	# 	public.megacamp_flood_risk,
	# 	public."BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan" 
	# 		JOIN public."Camp_pop_03_2019" 
	# 		ON public."BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan".cmp_name = public."Camp_pop_03_2019"."New_Camp_N"
	# 		JOIN public."T190310_Outline_RRC_Camp_A11" 
	# 		ON public."Camp_pop_03_2019"."New_Camp_N" = public."T190310_Outline_RRC_Camp_A11"."New_Camp_N"
	# WHERE 
	# 	ST_Intersects(public.megacamp_flood_risk.geom_4326, public."BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan".the_geom_centroid)
	# GROUP BY 1, 2, 3, 4
	# ORDER BY 1, 2, 3, 4	
	# '''

	# sql_hltfac = \
	# '''
	# SELECT 
	# 	public."Camp_pop_03_2019"."New_Camp_N" as camp,
	# 	public.megacamp_flood_risk.dn as risk_level,
	# 	COUNT(DISTINCT(public."cxb_health_facilities".fid)) as hltfac_at_risk_count
	# FROM 
	# 	public.megacamp_flood_risk,
	# 	public."cxb_health_facilities" 
	# 		JOIN public."Camp_pop_03_2019" 
	# 		ON public."cxb_health_facilities"."Camp_Name" = public."Camp_pop_03_2019"."New_Camp_N"
	# 		JOIN public."T190310_Outline_RRC_Camp_A11" 
	# 		ON public."Camp_pop_03_2019"."New_Camp_N" = public."T190310_Outline_RRC_Camp_A11"."New_Camp_N"
	# WHERE 
	# 	ST_Intersects(public.megacamp_flood_risk.geom_4326, public."cxb_health_facilities".the_geom)
	# GROUP BY 1, 2
	# ORDER BY 1, 2	
	# '''

	sql_shelter = \
	'''
	SELECT 
		public."Camp_pop_03_2019"."Upazila" as upazila,
		public."Camp_pop_03_2019"."Union" as union,
		public."Camp_pop_03_2019"."New_Camp_N" as camp,
		public."BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan".floodrisk_level as risk_level,
		COUNT(DISTINCT(public."BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan".fid)) as shelter_at_risk_count
	FROM 
		public."BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan" 
			JOIN public."Camp_pop_03_2019" 
			ON public."BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan".cmp_name = public."Camp_pop_03_2019"."New_Camp_N"
			JOIN public."T190310_Outline_RRC_Camp_A11" 
			ON public."Camp_pop_03_2019"."New_Camp_N" = public."T190310_Outline_RRC_Camp_A11"."New_Camp_N"
	where
		public."BGD_Camp_ShelterFootprint_UNOSAT_REACH_v1_Jan".floodrisk_level is not null
		and area_class='Structure'
	GROUP BY 1, 2, 3, 4
	ORDER BY 1, 2, 3, 4	
	'''

	sql_hltfac = \
	'''
	SELECT 
		public."Camp_pop_03_2019"."New_Camp_N" as camp,
		public.cxb_health_facilities.floodrisk_level as risk_level,
		COUNT(DISTINCT(public."cxb_health_facilities".fid)) as hltfac_at_risk_count
	FROM 
		public."cxb_health_facilities" 
			JOIN public."Camp_pop_03_2019" 
			ON public."cxb_health_facilities"."Camp_Name" = public."Camp_pop_03_2019"."New_Camp_N"
			JOIN public."T190310_Outline_RRC_Camp_A11" 
			ON public."Camp_pop_03_2019"."New_Camp_N" = public."T190310_Outline_RRC_Camp_A11"."New_Camp_N"
	where
		public."cxb_health_facilities".floodrisk_level is not null
	GROUP BY 1, 2
	ORDER BY 1, 2	
	'''

	FLOODRISK_LEVEL_CODES = [1, 2, 3]
	FLOODRISK_LEVEL_NAMES_SHORT = {
		1: 'low', 
		2: 'med', 
		3: 'high',
	}
	FLOODRISK_LEVEL_NAMES_SHORT_ORDER = [FLOODRISK_LEVEL_NAMES_SHORT[i] for i in FLOODRISK_LEVEL_CODES]
	FLOODRISK_LEVEL_NAMES_LONG = {
		'low': 'Low', 
		'med': 'Medium', 
		'high': 'High',
	}
	FLOODRISK_LEVEL_NAMES_SHORT_ORDER_PLUS_NOT_ATRISK = FLOODRISK_LEVEL_NAMES_SHORT_ORDER + ['not_at_risk']
	FLOODRISK_LEVEL_NAMES_LONG_PLUS_NOT_ATRISK = dict_ext(FLOODRISK_LEVEL_NAMES_LONG.copy()).updateget({'not_at_risk': 'Not at Risk'})

	query_shelter = BgdCampShelterfootprintUnosatReachV1Jan.objects.all()
	query_hltfac = CxbHealthFacilities.objects.all()

	total_shelters_per_camp = {camp['cmp_name']: camp for camp in query_shelter.values('cmp_name').annotate(total_shelter=Count('pk')).filter(area_class='Structure')}
	total_hltfac_per_camp = {camp['camp_name']: camp for camp in query_hltfac.values('camp_name').annotate(total_hltfac=Count('pk'))}

	floodrisk_hltfac_per_camp = dict_ext()
	with connections['datastore'].cursor() as cursor:
		for camp in query_to_dicts(cursor, sql_hltfac):
			floodrisk_hltfac_per_camp.path(camp['camp'])[camp['risk_level']] = {'hltfac_at_risk_count':camp['hltfac_at_risk_count']}

	with connections['datastore'].cursor() as cursor:
		floodrisks = [
			dict_ext(camp).updateget({
				'risk_name': FLOODRISK_LEVEL_NAMES_SHORT[camp['risk_level']],
				'shelter_count': total_shelters_per_camp[camp['camp']]['total_shelter'],
				'hltfac_count': total_hltfac_per_camp.get(camp['camp'], {}).get('total_hltfac') or 0,
				'hltfac_at_risk_count': floodrisk_hltfac_per_camp.pathget(camp['camp'], camp['risk_level'], 'hltfac_at_risk_count') or 0,
			})
			for camp in query_to_dicts(cursor, sql_shelter)
		]

	floodrisk = dict_ext({'child': dict_ext(), 'order': []})
	for camp in floodrisks:
		floodrisk['order'] += [camp.get('camp',''),] if camp.get('camp','') not in floodrisk['order'] else []
		row = floodrisk.path('child', camp.get('camp',''))
		row['camp'] = camp.get('camp','')
		row['union'] = camp.get('union','')
		row['upazila'] = camp.get('upazila','')
		row['shelter_'+camp.get('risk_name','').lower()] = camp.get('shelter_at_risk_count',0)
		row['hltfac_'+camp.get('risk_name','').lower()] = camp.get('hltfac_at_risk_count',0)
		row['hltfac_total'] = camp.get('hltfac_count',0)
		row['shelter_total'] = camp.get('shelter_count',0)
		row['shelter_at_risk'] = row.get('shelter_at_risk', 0) + camp.get('shelter_at_risk_count',0)
		row['hltfac_at_risk'] = row.get('hltfac_at_risk', 0) + camp.get('hltfac_at_risk_count',0)
		row['shelter_at_risk_pct'] = get_percent(row.get('shelter_at_risk', 0), row.get('shelter_total',0))
		row['hltfac_at_risk_pct'] = get_percent(row.get('hltfac_at_risk', 0), row.get('hltfac_total',0))
		row['shelter_not_at_risk'] = row['shelter_total'] - row['shelter_at_risk']
		row['hltfac_not_at_risk'] = row['hltfac_total'] - row['hltfac_at_risk']

	floodrisk['column_keys'] = {
		'counts':[
			'camp',
			'union',
			'upazila',
		],
		'sums': [
			'shelter_low',
			'shelter_med',
			'shelter_high',
			'hltfac_low',
			'hltfac_med',
			'hltfac_high',
			'shelter_at_risk',
			'shelter_not_at_risk',
			'shelter_total',
			'hltfac_at_risk',
			'hltfac_not_at_risk',
			'hltfac_total',		
		],
	}

	floodrisk['column_keys']['all'] = floodrisk['column_keys']['counts'] + floodrisk['column_keys']['sums']

	floodrisk['totals'] = dict_ext({
		key: len(set([i.get(key) for i in floodrisk['child'].values()])) 
		for key in floodrisk['column_keys']['counts']
	}).updateget({
		key: sum([i.get(key) or 0 for i in floodrisk['child'].values()])
		for key in floodrisk['column_keys']['sums']
	})

	floodrisk['totals'].updateget({
		'shelter_not_at_risk': floodrisk['totals']['shelter_total'] - floodrisk['totals']['shelter_at_risk'],
		'hltfac_not_at_risk': floodrisk['totals']['hltfac_total'] - floodrisk['totals']['hltfac_at_risk'],
		'shelter_at_risk_pct': get_percent(floodrisk['totals']['shelter_at_risk'], floodrisk['totals']['shelter_total']),
		'hltfac_at_risk_pct': get_percent(floodrisk['totals']['hltfac_at_risk'], floodrisk['totals']['hltfac_total']),
	})

	# floodrisk['totals'] = {
	# 	'camp': len(set([i.get('camp') for i in floodrisk['child'].values()])),
	# 	'union': len(set([i.get('union') for i in floodrisk['child'].values()])),
	# 	'upazila': len(set([i.get('upazila') for i in floodrisk['child'].values()])),
	# 	'shelter_low': sum([i.get('shelter_low') or 0 for i in floodrisk['child'].values()]),
	# 	'shelter_med': sum([i.get('shelter_med') or 0 for i in floodrisk['child'].values()]),
	# 	'shelter_high': sum([i.get('shelter_high') or 0 for i in floodrisk['child'].values()]),
	# 	'hltfac_low': sum([i.get('hltfac_low') or 0 for i in floodrisk['child'].values()]),
	# 	'hltfac_med': sum([i.get('hltfac_med') or 0 for i in floodrisk['child'].values()]),
	# 	'hltfac_high': sum([i.get('hltfac_high') or 0 for i in floodrisk['child'].values()]),
	# 	'shelter_at_risk': sum([i.get('shelter_at_risk') or 0 for i in floodrisk['child'].values()]),
	# 	'shelter_total': sum([i.get('shelter_total') or 0 for i in floodrisk['child'].values()]),
	# 	'hltfac_at_risk': sum([i.get('hltfac_at_risk') or 0 for i in floodrisk['child'].values()]),
	# 	'hltfac_total': sum([i.get('hltfac_total') or 0 for i in floodrisk['child'].values()]),
	# }

	TABLE_SHELTER_HLTFAC_COLUMN_ORDER = [
		'camp',
		'union',
		'upazila',
		'shelter_low',
		'shelter_med',
		'shelter_high',
		'hltfac_low',
		'hltfac_med',
		'hltfac_high',
		# 'shelter_at_risk',
		'shelter_at_risk_pct',
		# 'shelter_total',
		# 'hltfac_at_risk',
		'hltfac_at_risk_pct',
		# 'hltfac_total',	
	]

	response.updateget({
		'floodrisks': floodrisks,
		'total_shelters_per_camp': total_shelters_per_camp,
		'floodrisk_hltfac_per_camp': floodrisk_hltfac_per_camp,
		'floodrisk':floodrisk,
		'init_data': {
			'tables': {
				'table_shelter_hltfac': {
					'key': 'table_shelter_hltfac',
					'title': _('Shelter and Health Facilities in Flood Risk Area'),
					'column_keys': floodrisk['column_keys']['all'],
					'parentdata': [floodrisk['totals'][i] for i in TABLE_SHELTER_HLTFAC_COLUMN_ORDER],
					# 'parentdata':[
					# 		len(set([i.get('camp') for i in floodrisk['child'].values()])),
					# 		len(set([i.get('union') for i in floodrisk['child'].values()])),
					# 		len(set([i.get('upazila') for i in floodrisk['child'].values()])),
					# 		sum([i.get('shelter_low') or 0 for i in floodrisk['child'].values()]),
					# 		sum([i.get('shelter_med') or 0 for i in floodrisk['child'].values()]),
					# 		sum([i.get('shelter_high') or 0 for i in floodrisk['child'].values()]),
					# 		sum([i.get('hltfac_low') or 0 for i in floodrisk['child'].values()]),
					# 		sum([i.get('hltfac_med') or 0 for i in floodrisk['child'].values()]),
					# 		sum([i.get('hltfac_high') or 0 for i in floodrisk['child'].values()]),
					# 		sum([i.get('shelter_at_risk') or 0 for i in floodrisk['child'].values()]),
					# 		sum([i.get('shelter_total') or 0 for i in floodrisk['child'].values()]),
					# 		sum([i.get('hltfac_at_risk') or 0 for i in floodrisk['child'].values()]),
					# 		sum([i.get('hltfac_total') or 0 for i in floodrisk['child'].values()]),
					# 	],
					'child':[{
						'values':[floodrisk.path('child',i,key) for key in TABLE_SHELTER_HLTFAC_COLUMN_ORDER],
						# 'values':[
						# 	floodrisk.path('child',i,'camp'),
						# 	floodrisk.path('child',i,'union'),
						# 	floodrisk.path('child',i,'upazila'),
						# 	floodrisk.path('child',i,'shelter_low') or 0,
						# 	floodrisk.path('child',i,'shelter_med') or 0,
						# 	floodrisk.path('child',i,'shelter_high') or 0,
						# 	floodrisk.path('child',i,'hltfac_low') or 0,
						# 	floodrisk.path('child',i,'hltfac_med') or 0,
						# 	floodrisk.path('child',i,'hltfac_high') or 0,
						# 	floodrisk.path('child',i,'shelter_at_risk') or 0,
						# 	floodrisk.path('child',i,'shelter_total') or 0,
						# 	floodrisk.path('child',i,'hltfac_at_risk') or 0,
						# 	floodrisk.path('child',i,'hltfac_total') or 0,
						# ],
						'code': urllib.quote(floodrisk.path('child',i,'camp'))				
					} for i in floodrisk['order']]
				}
			},
			'charts': {
				'chart_pie_hltfac': {
					'key': 'chart_pie_hltfac',
					'title': _('Health Facilities'),
					# 'labels': [FLOODRISK_LEVEL_NAMES_LONG_PLUS_NOT_ATRISK[i] for i in FLOODRISK_LEVEL_NAMES_SHORT_ORDER_PLUS_NOT_ATRISK],
					'values': [
						[FLOODRISK_LEVEL_NAMES_LONG_PLUS_NOT_ATRISK[k], floodrisk['totals'].get('hltfac_'+k,0)] 
						for k in FLOODRISK_LEVEL_NAMES_SHORT_ORDER_PLUS_NOT_ATRISK
					],
				},
				'chart_pie_shelter': {
					'key': 'chart_pie_shelter',
					'title': _('Shelters'),
					'labels': [FLOODRISK_LEVEL_NAMES_LONG_PLUS_NOT_ATRISK[i] for i in FLOODRISK_LEVEL_NAMES_SHORT_ORDER_PLUS_NOT_ATRISK],
					'values': [
						[FLOODRISK_LEVEL_NAMES_LONG_PLUS_NOT_ATRISK[k], floodrisk['totals'].get('shelter_'+k,0)] 
						for k in FLOODRISK_LEVEL_NAMES_SHORT_ORDER_PLUS_NOT_ATRISK
					],
					# 'values': [floodrisk['totals'].get('shelter_'+k,0) for k in FLOODRISK_LEVEL_NAMES_SHORT_ORDER_PLUS_NOT_ATRISK],
				},
			}
		},
	})

	return response
