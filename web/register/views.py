from django.views.generic import TemplateView, View
from django.core import serializers
from django.contrib.gis.geos import Polygon
from django import http

from .models import LLSOA

class MapView(TemplateView):
    template_name = "map/map_view.html"


class MapAPIView(View):


    def get(self, request, *args, **kwargs):
        bbox = Polygon.from_bbox(
            [float(p) for p in request.GET.get('bbox').split(',')])
        qs = LLSOA.objects.exclude(area=None)
        qs = qs.filter(area__bboverlaps=bbox)
        qs = qs[:60]


        return http.HttpResponse(
            serializers.serialize(
                'geojson',
                qs,
                geometry_field='area',
            ))
