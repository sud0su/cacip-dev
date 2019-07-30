from django.conf.urls import include, patterns, url
from tastypie.api import Api

urlpatterns_getoverviewmaps = patterns(
    'dashboard.baseline.views',
    url(r'^baselineinfo$', 'getBaselineInfoVillages', name='getBaselineInfoVillages'),
)

urlpatterns = [
    url(r'^getOverviewMaps/', include(urlpatterns_getoverviewmaps)),
    url(r'^api/getoverviewmaps/', include(
        patterns(
            'dashboard.baseline.views',
            url(r'^baseline$', 'getBaselineInfoVillages', name='getBaselineInfoVillages'),
        )        
    )),
]
