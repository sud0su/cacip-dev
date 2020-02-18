from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from userstatistics.views import user_exclude

from django.db.models import Count
from geonode.layers.models import Layer
from geonode.maps.models import Map
from geonode.documents.models import Event, KnowledgehubDocument, News, Blog


def usercount(request):
    count = get_user_model().objects.exclude(username__in=user_exclude).count()
    data = {"usercount": count}
    return JsonResponse(data)


def countdata(request):
    layers_count = Layer.objects.all().count()
    maps_count = Map.objects.all().count()
    news_count = News.objects.all().count()
    blog_count = Blog.objects.all().count()
    event_count = Event.objects.all().count()

    queryset_doc = KnowledgehubDocument.objects.values('doc_type').annotate(doc_type_count=Count('doc_type'))

    docs = []
    for v in queryset_doc:
        docs.append({v['doc_type']: v['doc_type_count']})

    data = {
        "layers_count": layers_count, 
        "maps_count": maps_count, 
        "news_count": news_count, 
        "blogs_count": blog_count, 
        "events_count": event_count,
        "knowledgebase": docs
        }
    return JsonResponse(data)
