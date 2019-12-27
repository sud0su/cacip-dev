from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from userstatistics.views import user_exclude

def usercount(request):
    count = get_user_model().objects.exclude(username__in=user_exclude).count()
    data = {"usercount": count}
    return JsonResponse(data)

