from django.conf.urls import include, patterns, url
from tastypie.api import Api

urlpatterns_getoverviewmaps = patterns(
    'dashboard.floodrisk.views',
    url(r'^floodriskinfo$', 'getFloodRiskInfoVillages', name='getFloodRiskInfoVillages'),
)

urlpatterns = [
    url(r'^getOverviewMaps/', include(urlpatterns_getoverviewmaps)),
    url(r'^api/getoverviewmaps/', include(
        patterns(
            'dashboard.floodrisk.views',
            url(r'^floodrisk$', 'getFloodRiskInfoVillages', name='getFloodRiskInfoVillages'),
        )        
    )),
]
