from .models import matrix
from django.conf import settings
from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from geonode.people.models import Profile
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)

def savematrix(request=None, action='', resourcecode=settings.MATRIX_DEFAULT_MAP_CODE, resource=None):
    try:
        if not resource:
            from geonode.maps.views import _resolve_map, _PERMISSION_MSG_VIEW
            resource = _resolve_map(request, resourcecode, 'base.view_resourcebase', _PERMISSION_MSG_VIEW)
    except Exception as identifier:
        logger.warning('_resolve_map() failed using resource_code=%s, check settings.MATRIX_DEFAULT_MAP_CODE'%(settings.MATRIX_DEFAULT_MAP_CODE))
    else:
        if hasattr(request, 'user') and isinstance(request.user, Profile):
            user = request.user
        elif 'user' in request.GET:
            user = get_object_or_404(Profile, id=request.GET['user'])
        else:
            logger.warning('savematrix() needs valid user object')
            return
        queryset = matrix(user=user,resourceid=resource,action=action)
        queryset.save()
