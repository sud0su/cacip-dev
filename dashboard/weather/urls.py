from django.conf.urls import include, patterns, url
from tastypie.api import Api

urlpatterns_getoverviewmaps = patterns(
    'dashboard.weather.views',
    url(r'^weatherinfo$', 'getWeatherInfoVillages', name='getWeatherInfoVillages'),
)

urlpatterns = [
    url(r'^getOverviewMaps/', include(urlpatterns_getoverviewmaps)),
    url(r'^api/getoverviewmaps/', include(
        patterns(
            'dashboard.weather.views',
            url(r'^weather$', 'getWeatherInfoVillages', name='getWeatherInfoVillages'),
        )        
    )),
]
