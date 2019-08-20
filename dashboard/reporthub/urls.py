from django.conf.urls import include, patterns, url
from tastypie.api import Api

urlpatterns_getoverviewmaps = patterns(
    'dashboard.landslide.views',
    url(r'^landslideinfo$', 'getLandslideInfoVillages', name='getLandslideInfoVillages'),
)

urlpatterns = [
    url(r'^getOverviewMaps/', include(urlpatterns_getoverviewmaps)),
    url(r'^api/getoverviewmaps/', include(
        patterns(
            'dashboard.landslide.views',
            url(r'^landslide$', 'getLandslideInfoVillages', name='getLandslideInfoVillages'),
        )        
    )),
]
