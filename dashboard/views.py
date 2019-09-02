from django.shortcuts import render, redirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
# from geodb.geo_calc import getBaseline, getAccessibility, getEarthquake, getSecurity, getLandslideRisk, getQuickOverview, getDroughtRisk
# from geodb.geo_calc import getBaseline, getCommonUse, getProvinceSummary, getProvinceAdditionalSummary, getGeoJson
# from geodb.models import AdmbndaAdm1, AdmbndaAdm2
from django.shortcuts import HttpResponse
from matrix.views import savematrix
# from matrix.models import matrix, MatrixCertificate
# from dashboard.models import classmarker
from urlparse import urlparse
from geonode.maps.views import _resolve_map, _PERMISSION_MSG_VIEW
import json, os

# from wkhtmltopdf.views import PDFTemplateResponse
# import pdfkit
from geonode.people.models import Profile
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime
from django.utils.formats import dateformat

from django.conf import settings

import pdfcrowd
from PyPDF2 import PdfFileMerger, PdfFileReader
from StringIO import StringIO
import urllib2, urllib
from urlparse import parse_qs, urlsplit, urlunsplit
import re
from requests.utils import quote
from django.utils import translation

import time
import md5
import calendar
import datetime

# from avatar.templatetags.avatar_tags import avatar_print_url
from django.http import Http404

from .enumerations import DASHBOARD_META
from pprint import pprint
import importlib
from geonode.utils import set_query_parameter, dict_ext, list_ext, JSONEncoderCustom, include_section
from django.utils.translation import ugettext as _
# from graphos.renderers import flot, gchart
# from graphos.sources.simple import SimpleDataSource
# from geodb.enumerations import (
# 	DEPTH_TYPES_INVERSE,
# 	DEPTH_TYPES,
# 	HEALTHFAC_TYPES,
# 	LANDCOVER_TYPES,
# 	LANDCOVER_TYPES_GROUP,
# 	LANDCOVER_TYPES_GROUP_INVERSE,
# 	PROVINCESUMMARY_LANDCOVER_TYPES,
# 	LIKELIHOOD_INDEX,
# 	ROAD_TYPES,
# 	HEALTHFAC_TYPES_INVERSE,
# 	HEALTHFAC_GROUP7,
# 	HEALTHFAC_GROUP14,
# 	PANEL_TITLES,
# 	ROAD_INDEX,
# 	LANDCOVER_INDEX,
# )
from pychromeprint import print_from_urls
import copy 

def common(request):
	response = {}
	code = None
	flag = 'entireAfg'
	filterLock = None
	rawFilterLock = None
	kwarg = {}

	if 'page' not in request.GET:
		mutable = request.GET._mutable
		request.GET._mutable = True
		request.GET['page'] = 'baseline'
		request.GET._mutable = mutable

	if 'code' in request.GET:
		kwarg['areacode'] = code = request.GET['code'].strip()
		# kwarg['areatype'] = flag = 'currentProvince'

	if 'flag' in request.GET:
		filterLock = request.GET['filter']
		rawFilterLock = filterLock
		kwarg['areageom'] = filterLock = 'ST_GeomFromText(\''+filterLock+'\',4326)'
		# kwarg['areatype'] = flag = request.GET['flag']

	if 'pdf' in request.GET:
		# # mapCode = '700'
		# mapCode = settings.MATRIX_DEFAULT_MAP_CODE
		# try:
		# 	map_obj = _resolve_map(request, mapCode, 'base.view_resourcebase', _PERMISSION_MSG_VIEW)
		# except Exception as identifier:
		# 	print 'Warning: _resolve_map() failed using settings.MATRIX_DEFAULT_MAP_CODE'
		# else:
		# 	px = get_object_or_404(Profile, id=request.GET['user'])
		# 	queryset = matrix(user=px,resourceid=map_obj,action='Dashboard PDF '+request.GET['page'])
		# 	queryset.save()
		savematrix(request=request, action='Dashboard PDF %s'%(request.GET['page']))
	else:
		# # mapCode = '700'
		# mapCode = settings.MATRIX_DEFAULT_MAP_CODE
		# try:
		# 	map_obj = _resolve_map(request, mapCode, 'base.view_resourcebase', _PERMISSION_MSG_VIEW)
		# except Exception as identifier:
		# 	print 'Warning: _resolve_map() failed using settings.MATRIX_DEFAULT_MAP_CODE.'
		# else:
		# 	queryset = matrix(user=request.user,resourceid=map_obj,action='Dashboard '+request.GET['page'])
		# 	queryset.save()
		savematrix(request=request, action='Dashboard %s'%(request.GET['page']))

	page_name = request.GET['page']
	arg = [request]
	if page_name in ['accessibility', 'security']:
		arg = [request]
	page_name = 'avalancheforecast' if page_name == 'avalcheforecast' else page_name
	if page_name in ['drought']:
		if 'date' in request.GET:
			kwarg['date'] = request.GET.get('date')

	# get response data by importing module dynamically and run its dashboard functiion
	if page_name in DASHBOARD_META.get('DASHBOARD_TO_APP', {}).keys() \
	and DASHBOARD_META.get('DASHBOARD_TO_APP', {})[page_name] in DASHBOARD_META.get('DASHBOARD_APPS', []):

		# import module
		module = importlib.import_module('%s.views'%(DASHBOARD_META.get('DASHBOARD_TO_APP', {})[page_name]))
		# page_meta = dict_ext(module.get_dashboard_meta()).pathget('pagenames', page_name)

		# get dashboard meta info
		dashboard_meta = dict_ext(module.get_dashboard_meta())

		# get dashboard page meta info from dashboard meta
		page_meta = list_ext([v for v in dashboard_meta.pathget('pages') if v.get('name') == page_name]).get(0,dict_ext)

		# call dashboard page data retrieval function
		function_name = page_meta.get('function')
		response = dict_ext(getattr(module, function_name)(*arg, **kwarg) if function_name else {})

		response['dashboard_template'] = page_meta.get('template')
	# elif page_name == 'baseline':
	# 	response = dashboard_baseline(*arg, **kwarg)
	# 	response['dashboard_template'] = 'dash_baseline.html'
	# elif page_name == 'main':
	# 	response = getAllQuickOverview(*arg, **kwarg)
	# 	response['dashboard_template'] = 'dash_main.html'
	else:
		raise Http404("Dashboard page '%s' not found"%(request.GET['page']))

	# if request.GET['page'] == 'baseline':
	# 	response = getBaseline(request, filterLock, flag, code)
	# elif request.GET['page'] == 'floodforecast':
	# 	response = getFloodForecast(request, filterLock, flag, code)
	# elif request.GET['page'] == 'floodrisk':
	# 	response = getFloodRisk(request, filterLock, flag, code)
	# elif request.GET['page'] == 'avalancherisk':
	# 	response = getAvalancheRisk(request, filterLock, flag, code)
	# elif request.GET['page'] == 'avalcheforecast':
	# 	response = getAvalancheForecast(request, filterLock, flag, code)
	# elif request.GET['page'] == 'accessibility':
	# 	response = getAccessibility(request, rawFilterLock, flag, code)
	# elif request.GET['page'] == 'earthquake':
	# 	response = getEarthquake(request, filterLock, flag, code)
	# elif request.GET['page'] == 'security':
	# 	response = getSecurity(request, rawFilterLock, flag, code)
	# elif request.GET['page'] == 'landslide':
	# 	response = getLandslideRisk(request, filterLock, flag, code)
	# elif request.GET['page'] == 'main':
	# 	response = getQuickOverview(request, filterLock, flag, code)

	response['add_link'] = '&code='+str(code) if 'code' in request.GET else ''
	# if 'code' in request.GET:
	# 	response['add_link'] = '&code='+str(code)

	response['checked'] = request.GET['_checked'].split(",") if '_checked' in request.GET else []
	# response['checked'] = []
	# if '_checked' in request.GET:
	# 	response['checked'] = request.GET['_checked'].split(",") 

	response['jsondata'] = json.dumps(response, cls=JSONEncoderCustom)

	return response

# Create your views here.
def dashboard_detail(request):
	v2_folder = ''
	# user_logo = avatar_print_url(request.user,200)
	user_logo = {}

	headerparam_dict = {p: request.GET.get(p, '') for p in ['hideuserinfo','lang'] if p in request.GET}
	headerparam_dict.update({
		'onpdf': user_logo.get('onpdf'),
		'userlogo': user_logo.get('logo_url'),
		'name': request.user.first_name+' '+request.user.last_name,
		'cust_title': '%s %s'%('Dashboard',request.GET.get('page', '').title()),
		'organization': (request.user.organization or ''),
	})
	headerparam = urllib.urlencode(headerparam_dict)

	bodyparam_dict = {}
	if not request.GET.get('lang'):
		bodyparam_dict['lang'] = str(translation.get_language())
	bodyparam = urllib.urlencode(bodyparam_dict)

	# add '?page=baseline' to url if none exist
	if not request.GET.get('page'):
		currenturl = request.build_absolute_uri()
		return redirect(set_query_parameter(currenturl, 'page', 'baseline'))

	if 'pdf' in request.GET:
		try:
			domainpath = 'asdc.immap.org'+request.META.get('PATH_INFO')
			date_string = dateformat.format(datetime.date.today(), "Y-m-d")

			# create an API client instance
			client = pdfcrowd.Client(getattr(settings, 'PDFCROWD_UNAME', ''), getattr(settings, 'PDFCROWD_UPASS', ''))
			client.setPageWidth('8.3in')
			client.setPageHeight('11.7in')
			# client.setPageMargins('1in', '1in', '1in', '1in')
			client.setVerticalMargin("0.75in")
			client.setHorizontalMargin("0.25in")
			client.setHeaderUrl('http://asdc.immap.org/static/isdc/head_print/rep_header_vector.html?onpdf='+user_logo.get('onpdf','')+'&userlogo='+user_logo.get('logo_url','')+'&name='+request.user.first_name+'+'+request.user.last_name+'&cust_title=&organization='+(request.user.organization or '')+'&isodate='+date_string+'&'+headerparam)
			# convert a web page and store the generated PDF to a variable
			pdf = client.convertURI('http://'+str(domainpath)+'print?'+request.META.get('QUERY_STRING')+'&user='+str(request.user.id)+'&'+bodyparam)
			 # set HTTP response headers
			response = HttpResponse(content_type="application/pdf")
			response["Cache-Control"] = "no-cache"
			response["Accept-Ranges"] = "none"
			response["Content-Disposition"] = 'attachment; filename="'+request.GET['page']+'_'+date_string+'.pdf"'

			# send the generated PDF
			response.write(pdf)


		except pdfcrowd.Error, why:
			options = {

				# wkhtmltopdf settings
				# 'quiet': '',
				# 'page-size': 'A4',
				# 'page-width': '2550px',
				# 'page-height': '3300px',
				# 'dpi':300,
				# 'margin-left': 10,
				# 'margin-right': 10,
				# 'margin-bottom':10,
				# 'margin-top':25,
				# 'viewport-size':'800x600',
				# 'header-html': 'http://%s/static/isdc/head_print/rep_header.html?%s'%(request.META.get('HTTP_HOST'),headerparam),
				# 'header-html': 'http://'+request.META.get('HTTP_HOST')+'/static/rep_header(v2).html?name='+request.user.first_name+'-'+request.user.last_name+'&cust_title=&organization='+request.user.organization,
				# 'lowquality':'-'
				# 'disable-smart-shrinking':'-',
				# 'print-media-type':'-',
				# 'no-stop-slow-scripts':'-',

				# 'enable-javascript':'-',
				# 'window-status': 'ready',

				# pychrome settings
				# match screen to print layout and resolution as close as possible
				# in order for the map to scale correctly
				# for print debugging, uncomment ruler.png in custombase.html,
				# resolution in pixel, size in inches, time in seconds
				'screen-width':1024, # resolution when loading the page
				'screen-height':1024, # resolution when loading the page
				'paperWidth':8.27,
				'paperHeight':11.69,
				'marginTop':0.78,
				'marginBottom':0.45,
				'marginLeft':0.3,
				'marginRight':0.3,
				'scale':0.71, # 0.71 roughly equal to 1024 px print width on 1024 screen-width
				'after-document-loaded-delay': 1, # in seconds
				'timeout': 60, # in seconds
				'header-html': 'http://%s/static/epr_bgd/head_print/rep_header_chrome.html?%s'%(request.META.get('HTTP_HOST'),headerparam),
				'headerparam':headerparam_dict,
			}
			# if re.match('^/v2', request.path):
			# 	options['viewport-size'] = '1240x800'
			domainpath = request.META.get('HTTP_HOST')+request.META.get('PATH_INFO')
			url = 'http://'+str(domainpath)+'print?'+request.META.get('QUERY_STRING')+'&user='+str(request.user.id)+'&'+bodyparam
			# pdf = pdfkit.from_url(url, False, options=options)
			pdf = print_from_urls([url], print_option=options)
			date_string = dateformat.format(datetime.date.today(), "Y-m-d")
			response = HttpResponse(pdf,content_type='application/pdf')
			response['Content-Disposition'] = 'attachment; filename="'+request.GET['page']+'_'+date_string+'.pdf"'

		return response
	else:
		response = common(request)
		template = response['dashboard_template']
		# template = 'dashboard_base.html'
		# if request.resolver_match.namespace == 'v2':
		# 	template = 'v2/dashboard_base.html'
		return render_to_response(
			template,
			RequestContext(request, response))

def dashboard_print(request):
	# template = 'dashboard_base.html'
	# if request.resolver_match.namespace == 'v2':
	# 	template = 'v2/dashboard_base.html'
	if request.GET.get('lang'):
		translation.activate(request.GET.get('lang'))
	response = common(request)
	response['is_dashboard_print'] = True
	template = response['dashboard_template']
	return render_to_response(
		template,
		RequestContext(request, response))

def get_provinces(request):
	resource = AdmbndaAdm1.objects.all().values('prov_code','prov_na_en').order_by('prov_na_en')
	response = {'data': {'provinces': [], 'districts': []}}
	for i in resource:
		response['data']['provinces'].append({'name':i['prov_na_en'],'code':i['prov_code']})

	resource = AdmbndaAdm2.objects.all().values('dist_code','dist_na_en','prov_na_en').order_by('dist_na_en')
	for i in resource:
		response['data']['districts'].append({'name':i['dist_na_en'],'code':i['dist_code'],'parent':i['prov_na_en']})
	return HttpResponse(json.dumps(response), content_type='application/json')

@csrf_exempt
def dashboard_multiple(request):
	# user_logo = avatar_print_url(request.user,200)
	user_logo = {}
	urls = []
	# data = request.POST
	data = json.loads(request.body)
	domainpath = request.META.get('HTTP_HOST')
	domainpath += '/v2' if re.match('^/v2', request.path) else ''
	v2_folder = ''

	headerparam_dict = {p: request.GET.get(p, '') for p in ['hideuserinfo','lang'] if p in request.GET}
	headerparam = urllib.urlencode(headerparam_dict)

	bodyparam_dict = {}
	bodyparam_dict['lang'] = request.GET.get('lang') or str(translation.get_language())
	bodyparam = urllib.urlencode(bodyparam_dict)

	try:
		print request.META.get('HTTP_HOST'), request.META.get('PATH_INFO')
		date_string = dateformat.format(datetime.date.today(), "Y-m-d")

		# create an API client instance
		client = pdfcrowd.Client(getattr(settings, 'PDFCROWD_UNAME'), getattr(settings, 'PDFCROWD_UPASS'))
		client.setPageWidth('8.3in')
		client.setPageHeight('11.7in')
		# client.setPageMargins('1in', '1in', '1in', '1in')
		client.setVerticalMargin("0.75in")
		client.setHorizontalMargin("0.25in")
		client.setHeaderUrl('http://'+request.META.get('HTTP_HOST')+'/static/'+v2_folder+'rep_header_vector.html?onpdf='+user_logo.get('onpdf')+'&userlogo='+user_logo.get('logo_url')+'&name='+request.user.first_name+' '+request.user.last_name+'&cust_title='+quote(data['mapTitle'].encode('utf-8'))+'&organization='+request.user.organization+'&isodate='+date_string+'&'+headerparam)
		# convert a web page and store the generated PDF to a variable

		# get map pdf
		req = urllib2.Request(data['mapUrl'])
		req.add_unredirected_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.107 Safari/537.36')
		fh = urllib2.urlopen(req)
		f = fh.read()

		merger = PdfFileMerger()

		merger.append(StringIO(f))

		for i in data['urls']:
			if i is not None and i != '':
				# urls.append(str('http://'+domainpath+'/dashboard/print'+i+'&user='+str(request.user.id)))
				pdf = client.convertURI(str('http://'+domainpath+'/dashboard/print'+i+'&user='+str(request.user.id)+'&'+bodyparam))
				merger.append(StringIO(pdf))

		 # set HTTP response headers
		# response = HttpResponse(content_type="application/pdf")
		# response["Cache-Control"] = "no-cache"
		# response["Accept-Ranges"] = "none"
		# response["Content-Disposition"] = 'attachment; filename="'+data['fileName']+'.pdf"'

		# send the generated PDF
		# merger.write(response)
		# return response
		merger.write(getattr(settings, 'PRINT_CACHE_PATH')+data['mapUrl'].split('/')[-1])
		return HttpResponse(json.dumps({'filename':data['mapUrl'].split('/')[-1]}), content_type='application/json')

	except pdfcrowd.Error, why:
		options = {
			'quiet': '',
			'page-size': 'A4',
			'page-width': '2550px',
			'page-height': '3300px',
			'dpi':300,			
			# 'margin-left': 10,
			# 'margin-right': 10,
			'margin-bottom':10,
			'margin-top':25,
			# 'viewport-size':'800x600',
			'header-html': 'http://'+request.META.get('HTTP_HOST')+'/static/'+v2_folder+'rep_header.html?onpdf='+user_logo.get('onpdf')+'&userlogo='+user_logo.get('logo_url')+'&name='+request.user.first_name+' '+request.user.last_name+'&cust_title='+quote(data['mapTitle'].encode('utf-8'))+'&organization='+request.user.organization+'&'+headerparam,
			# 'lowquality':'-',
			# 'disable-smart-shrinking':'-',
			# 'print-media-type':'-',
			# 'no-stop-slow-scripts':'-',
			# 'enable-javascript':'-',
			'after-document-loaded-delay': 25000,
			# 'window-status': 'ready',
			'encoding': "UTF-8",
		}

		# f = urllib.request.urlopen(data['mapUrl']).read()
		req = urllib2.Request(data['mapUrl'])
		req.add_unredirected_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.107 Safari/537.36')
		fh = urllib2.urlopen(req)
		f = fh.read()

		merger = PdfFileMerger()
		merger.append(StringIO(f))

		for i in data['urls']:
			if i is not None and i != '':
				urls.append(str('http://'+domainpath+'/dashboard/print'+i+'&user='+str(request.user.id)+'&'+bodyparam))

		# pdf = pdfkit.from_url(urls, False, options=options)
		pdf = print_from_urls(urls, print_option=options)
		merger.append(StringIO(pdf))


		# resp = HttpResponse(pdf,content_type='application/pdf')
		# resp = HttpResponse(content_type="application/pdf")
		# resp["Cache-Control"] = "no-cache"
		# resp["Accept-Ranges"] = "none"
		# resp['Content-Disposition'] = 'attachment; filename="'+data['fileName']+'.pdf"'

		merger.write(getattr(settings, 'PRINT_CACHE_PATH')+data['mapUrl'].split('/')[-1])
		return HttpResponse(json.dumps({'filename':data['mapUrl'].split('/')[-1]}), content_type='application/json')

def downloadPDFFile(request):
	with open(getattr(settings, 'PRINT_CACHE_PATH')+request.GET['filename'], 'r') as pdf:
		response = HttpResponse(pdf.read(),content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="'+quote(request.GET['filenameoutput'].encode('utf-8'))+'.pdf"'
		return response

def classmarkerRedirect(request):
	return redirect('https://www.classmarker.com/online-test/start/?quiz=mft579f02fe604fb&cm_user_id='+request.user.username+'&cm_fn='+request.user.first_name+'&cm_ln='+request.user.last_name+'&cm_e='+request.user.email)

def classmarkerInsert(request):
	# classmarker
	# print request.GET
	# data = get_object_or_404(classmarker, cm_user_id=request.GET['cm_user_id'])
	data = classmarker.objects.filter(cm_user_id=request.GET['cm_user_id'])
	cm_ts = request.GET['cm_ts']
	cm_tsa = request.GET['cm_tsa']
	cm_tp = request.GET['cm_tp']

	if data.count()>0:
		if data[0].cm_ts > float(cm_ts):
			cm_ts = data[0].cm_ts
		if data[0].cm_tsa > float(cm_tsa):
			cm_tsa = data[0].cm_tsa
		if data[0].cm_tp > float(cm_tp):
			cm_tp = data[0].cm_tp

		p = classmarker(pk=data[0].pk,cm_ts=cm_ts,cm_tsa=cm_tsa,cm_tp=cm_tp,cm_td=request.GET['cm_td'],cm_fn=request.GET['cm_fn'],cm_ln=request.GET['cm_ln'],cm_e=request.GET['cm_e'],cm_user_id=request.GET['cm_user_id'])
	else:
		p = classmarker(cm_ts=cm_ts,cm_tsa=cm_tsa,cm_tp=cm_tp,cm_td=request.GET['cm_td'],cm_fn=request.GET['cm_fn'],cm_ln=request.GET['cm_ln'],cm_e=request.GET['cm_e'],cm_user_id=request.GET['cm_user_id'])

	p.save()
	return HttpResponse({}, content_type='application/json')

def classmarkerGet():
	api_name = 'getUsersData'
	api_key = 'QPCkKLbJ5XemMe8Kei6oLD0ZE0w1JfOa'
	api_secret = '1WpKiVZKTD4gnAwwNzk0dO9MT1nDFcjF87Vmzv4S'
	# d = datetime.utcnow()
	# ts = calendar.timegm(d.utctimetuple())
	ts = int(time.time())
	from_ts = int(time.mktime((2017, 11, 15, 0, 0, 0, 0, 0, 0)))
	signature = md5.new(api_key + api_secret + str(ts));
	# url = 'https://api.classmarker.com/v1/groups/315743/tests/673903/recent_results.json?api_key=%s&signature=%s&timestamp=%s&finishedAfterTimestamp=%s' %(api_key,signature.hexdigest(),str(ts),str(from_ts))
	url = 'https://api.classmarker.com/v1/links/recent_results.json?api_key=%s&signature=%s&timestamp=%s' %(api_key,signature.hexdigest(),str(ts))
	# print url
	data = urllib.urlopen(url)
	for i in data:
		result = json.loads(i)
		# print result['results']
		for x in result['results']:
			available_certified_users = MatrixCertificate.objects.filter(pk=x['result']['email'])
			if available_certified_users.count()>0:
				if x['result']['percentage']>available_certified_users[0].percentage:
					available_certified_users[0].first = x['result']['first']
					available_certified_users[0].last = x['result']['last']
					available_certified_users[0].percentage = x['result']['percentage']
					available_certified_users[0].points_score = x['result']['points_score']
					available_certified_users[0].points_available = x['result']['points_available']
					available_certified_users[0].time_started = x['result']['time_started']
					available_certified_users[0].time_finished = x['result']['time_finished']
					available_certified_users[0].cm_user_id = x['result']['cm_user_id']
					available_certified_users[0].save()
					# print available_certified_users
			else:
				p = MatrixCertificate(pk=x['result']['email'])	
				p.first = x['result']['first']
				p.last = x['result']['last']
				p.percentage = x['result']['percentage']
				p.points_score = x['result']['points_scored']
				p.points_available = x['result']['points_available']
				p.time_started = x['result']['time_started']
				p.time_finished = x['result']['time_finished']
				p.cm_user_id = x['result']['cm_user_id']
				p.save()	
				# print p

def dashboard_baseline(request, filterLock, flag, code, includes=[], excludes=[], response=dict_ext()):

	if include_section('getCommonUse', includes, excludes):
		response = dict_ext(getCommonUse(request, flag, code))
	# baseline = getBaseline(request, filterLock, flag, code, includes, excludes, inject, response=dict(response))
	response['source'] = baseline = response.pathget('cache','getBaseline','baseline') or getBaseline(request, filterLock, flag, code, includes, excludes, response=dict_ext(response))
	panels = response.path('panels')

	response['healthfacility'] = {k:baseline['healthfacility'].get(k,0) for k in HEALTHFAC_GROUP7}
	response['healthfacility']['other'] += sum([v or 0 for k,v in baseline['healthfacility'].items() if k not in HEALTHFAC_GROUP7])
	# response.path('panels','healthfacility')['other'] = sum([baseline['healthfacility'].get(k) for k in ['rh','sh','mh','datc','pic','other','mc','mht']])

	# for sub in ['pop','area','building']:
	# 	response.path('panels')[sub+'_lc'] = baseline[sub+'_lc']
	# 	for k,v in LANDCOVER_TYPES_GROUP.items():
	# 		response.path('panels',sub+'_lcgroup')[k] = sum([baseline[sub+'_lc'].get(i) or 0 for i in v])

	transfers = ['pop_total','area_total','building_total','settlement_total','healthfacility_total','road_total','GeoJson']
	response.update({key:baseline[key] for key in transfers if key in baseline})
	response['references'] = {'HEALTHFAC_TYPES': HEALTHFAC_TYPES,'LANDCOVER_TYPES': LANDCOVER_TYPES,'ROAD_TYPES': ROAD_TYPES,}

	# convert to pre sort list format 
	total_titles = {'pop':'Total Population','building':'Total Buildings','area':'Total Area (km2)','settlement':'Number of Settlements','healthfacility':'Health Facilities','road':'Total Length of Road (km)'}
	charts = dict_ext({
		'pop_lc': {
			'title':_('Population Graph'),
			'labels':[LANDCOVER_TYPES[k] for k in LANDCOVER_INDEX.values()],
			'values':[baseline['pop_lc'].get(k) or 0 for k in LANDCOVER_INDEX.values()]
		},
		'area_lc': {
			'title':_('Area Graph'),
			'labels':[LANDCOVER_TYPES[k] for k in LANDCOVER_INDEX.values()],
			'values':[baseline['area_lc'].get(k) or 0 for k in LANDCOVER_INDEX.values()]
		},
		'building_lc': {
			'title':_('Building Graph'),
			'labels':[LANDCOVER_TYPES[k] for k in LANDCOVER_INDEX.values()],
			'values':[baseline['building_lc'].get(k) or 0 for k in LANDCOVER_INDEX.values()]
		},
		'healthfacility': {
			'title':_('Health Facilities Graph'),
			'labels':[HEALTHFAC_TYPES[k] for k in HEALTHFAC_GROUP7],
			'values':[response['healthfacility'].get(k) or 0 for k in HEALTHFAC_GROUP7]
		},
		'road': {
			'title':_('Road Network Graph'),
			'labels':[ROAD_TYPES[k] for k in ROAD_INDEX.values()],
			'values':[baseline['road'].get(k) or 0 for k in ROAD_INDEX.values()]
		},
	})

	panels['total'] = {
			'title':_('Total'),
			'labels':[total_titles[k] for k in ['pop','building','area','settlement','healthfacility','road']],
			'values':[baseline.get(k+'_total') or 0 for k in ['pop','building','area','settlement','healthfacility','road']]
	}

	for v in panels.values():
		v['total'] = sum(v['values'])

	panels['charts'] = charts.within('pop_lc','area_lc','building_lc','healthfacility','road')
	# childs = dict_ext({
	# 	'pop': [{'title':LANDCOVER_TYPES[k],'value':baseline['pop_lc'].get(k,0)} for k in LANDCOVER_INDEX.values()],
	# 	'area': [{'title':LANDCOVER_TYPES[k],'value':baseline['area_lc'].get(k,0)} for k in LANDCOVER_INDEX.values()],
	# 	'building': [{'title':LANDCOVER_TYPES[k],'value':baseline['building_lc'].get(k,0)} for k in LANDCOVER_INDEX.values()],
	# 	'healthfacility': [{'title':HEALTHFAC_TYPES[k],'value':response.path('panels')['healthfacility'].get(k,0)} for k in HEALTHFAC_GROUP14],
	# 	'road': [{'title':ROAD_TYPES[k],'value':baseline['road'].get(k,0)} for k in ROAD_INDEX.values()],
	# 	'total': [{'title':total_titles[k],'value':baseline.get(k+'_total',0)} for k in ['pop','building','area','settlement','healthfacility','road']],
	# })
	# panels = {k:{'title': PANEL_TITLES[k],'child': childs[k],'total': baseline[k+'_total'],} for k in ['pop','area','building','healthfacility','road']}
	# panels['total'] = {'title':'Totals','child': childs['total']} 

	tables = dict_ext()
	
	if include_section('adm_lc', includes, excludes):
		response['adm_lc'] = baseline['adm_lc']
		tables['adm_lcgroup_pop_area'] = {
			'title':_('Overview of Population and Area'),
			'parentdata':[response['parent_label'],baseline['building_total'],baseline['settlement_total'],baseline['pop_lcgroup']['built_up'],baseline['area_lcgroup']['built_up'],baseline['pop_lcgroup']['cultivated'],baseline['area_lcgroup']['cultivated'],baseline['pop_lcgroup']['barren'],baseline['area_lcgroup']['barren'],baseline['pop_total'],baseline['area_total'],],
			'child':[{
				'values':[v['na_en'],v['total_buildings'],v['settlements'],v['built_up_pop'],v['built_up_area'],v['cultivated_pop'],v['cultivated_area'],v['barren_pop'],v['barren_area'],v['Population'],v['Area'],],
				'code':v['code'],
			} for v in baseline['adm_lc']],
		}

	if include_section('adm_hlt_road', includes, excludes):
		response['adm_hlt_road'] = baseline['adm_hlt_road']
		hlt_other = sum([v for k,v in baseline['healthfacility'].items() if k not in HEALTHFAC_GROUP7]) + baseline['healthfacility']['other']
		tables['adm_healthfacility'] = {
			'title':_('Health Facility'),
			'parentdata':[response['parent_label'],baseline['healthfacility']['h1'],baseline['healthfacility']['h2'],baseline['healthfacility']['h3'],baseline['healthfacility']['chc'],baseline['healthfacility']['bhc'],baseline['healthfacility']['shc'],hlt_other,baseline['healthfacility_total'],],
			'child':[{
				'values':[v['na_en'],v['hlt_h1'],v['hlt_h2'],v['hlt_h3'],v['hlt_chc'],v['hlt_bhc'],v['hlt_shc'],v['hlt_others'],v['hlt_total'],],
				'code':v['code'],
			} for v in baseline['adm_hlt_road']],
		}

		tables['adm_road'] = {
			'title':_('Road Network'),
			'parentdata':[response['parent_label'],baseline['road']['highway'],baseline['road']['primary'],baseline['road']['secondary'],baseline['road']['tertiary'],baseline['road']['residential'],baseline['road']['track'],baseline['road']['path'],baseline['road_total'],],
			'child':[{
				'values':[v['na_en'],v['road_highway'],v['road_primary'],v['road_secondary'],v['road_tertiary'],v['road_residential'],v['road_track'],v['road_path'],v['road_total'],],
				'code':v['code'],
			} for v in response['adm_hlt_road']],
		}

	panels['tables'] = tables.within('adm_lcgroup_pop_area','adm_healthfacility','adm_road')

	# response['panels_list'] = [panels[k] for k in ['total','pop','building','area','adm_lcgroup_pop_area','adm_healthfacility','healthfacility','road','adm_road']]

	if include_section('GeoJson', includes, excludes):
		response['GeoJson'] = geojsonadd(response)

	# dataLC = []
	# dataLC.append([_('landcover type'),_('population'), { 'role': 'annotation' },_('buildings'), { 'role': 'annotation' },_('area (km2)'), { 'role': 'annotation' }])
	# # dataLC.append([_('Built-up'),round((response['built_up_pop'] or 0)/(response['Population'] or 0)*100,0), response['built_up_pop'],round((response['built_up_buildings'] or 0)/(response['Buildings'] or 0)*100,0), response['built_up_buildings'], round((response['built_up_area'] or 0)/(response['Area'] or 0)*100,0), response['built_up_area'] ])
	# # dataLC.append([_('Cultivated'),round((response['cultivated_pop'] or 0)/(response['Population'] or 0)*100,0), response['cultivated_pop'],round((response['cultivated_buildings'] or 0)/(response['Buildings'] or 0)*100,0), response['cultivated_buildings'], round((response['cultivated_area'] or 0)/(response['Area']*100 or 0),0), response['cultivated_area'] ])
	# # dataLC.append([_('Barren/Rangeland'),round((response['barren_pop'] or 0)/(response['Population'] or 0)*100,0), response['barren_pop'],round((response['barren_buildings'] or 0)/(response['Buildings'] or 0)*100,0), response['barren_buildings'], round((response['barren_area'] or 0)/(response['Area'] or 0)*100,0), response['barren_area'] ])
	# response['landcover_chart'] = gchart.BarChart(
	# 	SimpleDataSource(data=dataLC),
	# 	html_id="pie_chart1",
	# 	options={
	# 		'title': _('Landcover Population and area overview'),
	# 		# 'subtitle': 'figure as percent from total population and area',
	# 		'width': 450,
	# 		'height': 300,
	# 		# 'legend': { 'position': 'none' },
	# 		# 'chart': { 'title': 'Landcover Population and area overview', 'subtitle': 'figure as percent from total population and area' },
	# 		'bars': 'horizontal',
	# 		'axes': {
	# 			'x': {
	# 			  '0': { 'side': 'top', 'label': _('Percentage')}
	# 			},

	# 		},
	# 		'bar': { 'groupWidth': '90%' },
	# 		'chartArea': {'width': '50%'},
	# 		'titleX':_('percentages from total population, buildings & area'),
	# })
	# response.path('total')['hltfac'] = response.path('total')['hltfac'] or 0.000001
	# # if total['hltfac']==0:
	# #     total['hltfac'] = 0.000001

	# dataHLT = []
	# hf = response['panel']['hltfac']
	# total = response['total']
	# dataHLT.append([_('health facility type'),_('percent of health facility'), { 'role': 'annotation' }])
	# dataHLT.append([_('H1'),round(hf['h1']/total['hltfac']*100,0), hf['h1'] ])
	# dataHLT.append([_('H2'),round(hf['h2']/total['hltfac']*100,0), hf['h2'] ])
	# dataHLT.append([_('H3'),round(hf['h3']/total['hltfac']*100,0), hf['h3'] ])
	# dataHLT.append([_('CHC'),round(hf['chc']/total['hltfac']*100,0), hf['chc'] ])
	# dataHLT.append([_('BHC'),round(hf['bhc']/total['hltfac']*100,0), hf['bhc'] ])
	# dataHLT.append([_('SHC'),round(hf['shc']/total['hltfac']*100,0), hf['shc'] ])
	# dataHLT.append([_('Others'),round(hf['others']/total['hltfac']*100,0), hf['others'] ])
	# response['hlt_chart'] = gchart.BarChart(
	# 	SimpleDataSource(data=dataHLT),
	# 	html_id="pie_chart2",
	# 	options={
	# 		'title': _('Health facilities overview'),
	# 		# 'subtitle': 'figure as percent from total population and area',
	# 		'width': 450,
	# 		'height': 300,
	# 		'legend': { 'position': 'none' },
	# 		# 'chart': { 'title': 'Landcover Population and area overview', 'subtitle': 'figure as percent from total population and area' },
	# 		'bars': 'horizontal',
	# 		'axes': {
	# 			'x': {
	# 			  '0': { 'side': 'top', 'label': _('Percentage')}
	# 			},

	# 		},
	# 		'bar': { 'groupWidth': '90%' },
	# 		'chartArea': {'width': '50%'},
	# 		'titleX':_('percentages from total health facilities'),
	# })

	# dataRDN = []
	# road = response['panel']['road']
	# dataRDN.append([_('road network type'),_('percent of road network'), { 'role': 'annotation' }])
	# dataRDN.append([_('Highway'),round(road['highway']/total['roadnetwork']*100,0), road['highway'] ])
	# dataRDN.append([_('Primary'),round(road['primary']/total['roadnetwork']*100,0), road['primary'] ])
	# dataRDN.append([_('Secondary'),round(road['secondary']/total['roadnetwork']*100,0), road['secondary'] ])
	# dataRDN.append([_('Tertiary'),round(road['tertiary']/total['roadnetwork']*100,0), road['tertiary'] ])
	# dataRDN.append([_('Residential'),round(road['residential']/total['roadnetwork']*100,0), road['residential'] ])
	# dataRDN.append([_('Track'),round(road['track']/total['roadnetwork']*100,0), road['track'] ])
	# dataRDN.append([_('Path'),round(road['path']/total['roadnetwork']*100,0), road['path'] ])
	# dataRDN.append([_('River crossing'),round(road['river_crossing']/total['roadnetwork']*100,0), road['river_crossing'] ])
	# dataRDN.append([_('Bridge'),round(road['bridge']/total['roadnetwork']*100,0), road['bridge'] ])
	# response['rdn_chart'] = gchart.BarChart(
	# 	SimpleDataSource(data=dataRDN),
	# 	options={
	# 		'title': _('Road network overview'),
	# 		# 'subtitle': 'figure as percent from total population and area',
	# 		'width': 450,
	# 		'height': 300,
	# 		'legend': { 'position': 'none' },
	# 		# 'chart': { 'title': 'Landcover Population and area overview', 'subtitle': 'figure as percent from total population and area' },
	# 		'bars': 'horizontal',
	# 		'axes': {
	# 			'x': {
	# 			  '0': { 'side': 'top', 'label': _('Percentage')}
	# 			},

	# 		},
	# 		'bar': { 'groupWidth': '90%' },
	# 		'chartArea': {'width': '50%'},
	# 		'titleX':_('percentages from total length of road network'),
	# })

	# print response['poi_points']
	# print response['additional_child']
	# for i in response['additional_child']:
	#     test = [item for item in response['poi_points'] if item['code'] == i['code']][0]
	#     i['x'] = test['x']
	#     i['y'] = test['y']

	# response['additional_child'] = json.dumps(response['additional_child'])
	# print response['additional_child']

	# if include_section('GeoJson', includes, excludes):
	#     response['GeoJson'] = json.dumps(getGeoJson(request, flag, code))
		# response['GeoJson'] = getGeoJson(request, flag, code)

	#print 'It took', time.time()-start, 'seconds.'

	# response['references'] = {'HEALTHFAC_TYPES': HEALTHFAC_TYPES,'LANDCOVER_TYPES': LANDCOVER_TYPES,'ROAD_TYPES': ROAD_TYPES,}

	return response

def geojsonadd(response=dict_ext()):

	boundary = response['GeoJson']
	for feature in boundary.get('features',[]):

		#  Checking if it's in a district
		if response['areatype'] == 'district':
			response['set_jenk_divider'] = 1
			feature['properties']['Population']=response['source']['pop_total']
			feature['properties']['Buildings']=response['source']['building_total']
			feature['properties']['Area']=response['source']['area_total']
			feature['properties']['na_en']=response['parent_label']
			feature['properties'].update({'hlt_'+k:v for k,v in response['source']['healthfacility'].items()})
			feature['properties']['hlt_total']=response['source']['healthfacility_total']
			feature['properties'].update({'road_'+k:v for k,v in response['source']['road'].items()})
			feature['properties']['road_total']=response['source']['road_total']
		else:
			response['set_jenk_divider'] = 7

			feature['properties']['all_population']=response['source']['pop_total']
			feature['properties']['all_buildings']=response['source']['building_total']
			feature['properties']['all_area']=response['source']['pop_total']

			for data in response.get('adm_lc'):
				if (feature['properties']['code']==data['code']):
					feature['properties']['Population']=data['Population']
					feature['properties']['Buildings']=data['total_buildings']
					feature['properties']['Area']=data['Area']

			for data in response.get('adm_hlt_road'):
				if (feature['properties']['code']==data['code']):
					feature['properties']['na_en']=data['na_en']
					feature['properties']['hlt_h1']=data['hlt_h1']
					feature['properties']['hlt_h2']=data['hlt_h2']
					feature['properties']['hlt_h3']=data['hlt_h3']
					feature['properties']['hlt_chc']=data['hlt_chc']
					feature['properties']['hlt_bhc']=data['hlt_bhc']
					feature['properties']['hlt_shc']=data['hlt_shc']
					feature['properties']['hlt_others']=data['hlt_others']
					feature['properties']['hlt_total']=data['hlt_total']
					feature['properties']['road_highway']=data['road_highway']
					feature['properties']['road_primary']=data['road_primary']
					feature['properties']['road_secondary']=data['road_secondary']
					feature['properties']['road_tertiary']=data['road_tertiary']
					feature['properties']['road_residential']=data['road_residential']
					feature['properties']['road_track']=data['road_track']
					feature['properties']['road_path']=data['road_path']
					feature['properties']['road_total']=data['road_total']

	return boundary

def getAllQuickOverview(request, filterLock, flag, code, includes=[], excludes=[]):
	# response = dict_ext()
	# tempData = getShortCutData(flag,code)
	# response['Population']= tempData['Population']
	# response['Area']= tempData['Area']
	# response['Buildings']= tempData['total_buildings']
	# response['settlement']= tempData['settlements']
	response = dict_ext(getCommonUse(request, flag, code))
	# if include_section('', includes, excludes):
	# 	baseline = getBaseline(request, filterLock, flag, code, 
	# 		excludes=['getProvinceSummary', 'getProvinceAdditionalSummary'],
	# 		response=initresponse,
	# 		inject={
	# 			'forward':True,
	# 			'Population': tempData['Population'],
	# 			'Area': tempData['Area'],
	# 			'total_buildings': tempData['total_buildings'],
	# 			'settlements': tempData['settlements']
	# 		}
	# 	)
	# baseline = getBaseline(request, filterLock, flag, code, baselineonly=False)
	response.update({
		'cache': {
			'getBaseline': getBaseline(request, filterLock, flag, code, baselineonly=False),
		},
	})

	response['quickoverview'] = [dict_ext({'app':'geodb'}).updateget(getQuickOverview(request, filterLock, flag, code, response=copy.copy(response)))]

	# add response from optional modules
	for app in settings.QUICKOVERVIEW_MODULES:
		module = importlib.import_module(app+'.views')
		response['quickoverview'] += [dict_ext({'app':app}).updateget(module.getQuickOverview(request, filterLock, flag, code, response=copy.copy(response)))]
		
		# response.update(getFloodForecastMatrix(filterLock, flag, code, includes=['flashflood_forecast_risk_pop']))
		# response.update(getFloodForecast(request, filterLock, flag, code, excludes=['getCommonUse','detail']))
		# response.update(getRawFloodRisk(filterLock, flag, code, excludes=['landcoverfloodrisk']))
		# response.update(getRawAvalancheForecast(request, filterLock, flag, code))
		# response.update(getRawAvalancheRisk(filterLock, flag, code))
		# response.update(getLandslideRisk(request, filterLock, flag, code, includes=['lsi_immap']))
		# response.update(getEarthquake(request, filterLock, flag, code, excludes=['getListEQ']))

		# response.update(GetAccesibilityData(filterLock, flag, code, includes=['CaptAirdrmImmap', 'CaptHltfacTier1Immap', 'CaptHltfacTier2Immap', 'CaptAdm1ItsProvcImmap', 'CapaGsmcvr']))
		# response['pop_coverage_percent'] = int(round((response['pop_on_gsm_coverage']/response['Population'])*100,0))

	# if include_section('getSAMParams', includes, excludes):
	#     rawFilterLock = filterLock if 'flag' in request.GET else None
	#     if 'daterange' in request.GET:
	#         daterange = request.GET.get('daterange')
	#     elif 'daterange' in request.POST:
	#         daterange = request.POST.get('daterange')
	#     else:
	#         enddate = datetime.date.today()
	#         startdate = datetime.date.today() - datetime.timedelta(days=365)
	#         daterange = startdate.strftime("%Y-%m-%d")+','+enddate.strftime("%Y-%m-%d")
	#     main_type_raw_data = getSAMParams(request, daterange, rawFilterLock, flag, code, group='main_type', includeFilter=True)
	#     response['incident_type'] = (i['main_type'] for i in main_type_raw_data)
	#     if 'incident_type' in request.GET:
	#         response['incident_type'] = request.GET['incident_type'].split(',')
	#     response['incident_type_group']=[]
	#     for i in main_type_raw_data:
	#         response['incident_type_group'].append({'count':i['count'],'injured':i['injured'],'violent':i['violent']+i['affected'],'dead':i['dead'],'main_type':i['main_type'],'child':list(getSAMIncident(request, daterange, rawFilterLock, flag, code, 'type', i['main_type']))})
	#     response['main_type_child'] = getSAMParams(request, daterange, rawFilterLock, flag, code, 'main_type', False)

	# if include_section('GeoJson', includes, excludes):
	# 	response['GeoJson'] = getGeoJson(request, flag, code)

	return response

def getQuickOverview(request, filterLock, flag, code, response=dict_ext()):
	dashboard_baseline_response = dashboard_baseline(request, filterLock, flag, code, includes=[''], response=response)
	return {
		'templates':{
			'panels':'dash_qoview_baseline.html',
			'row_totals':'dash_baseline_row_totals.html',
		},
		'data':{
			'panels':dict_ext(dashboard_baseline_response).pathget('panels'),
		},
	}
