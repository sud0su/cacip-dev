from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

import requests

def get_dashboard_meta():
	return {
		'pages': [
			{
				'name': 'weather',
				# 'function': None, 
				'template': 'dash_weather.html',
				'menutitle': 'Weather',
			},
		],
		'menutitle': 'Weather',
	}

# moved from isdc_geodb.views

def getWeatherInfoVillages(request):
    template = './weatherinfo.html'
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
