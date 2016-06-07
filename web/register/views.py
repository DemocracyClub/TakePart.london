from django.views.generic import TemplateView, View
from django.core import serializers
from django.contrib.gis.geos import Polygon
from django.shortcuts import redirect
from django import http

import requests

from .models import LLSOA

class MapView(TemplateView):
    template_name = "map/map_view.html"

    def get(self, request, *args, **kwargs):
        if 'postcode' in request.GET:
            try:
                req = requests.get(
                    "http://mapit.democracyclub.org.uk/postcode/{}".format(
                        request.GET['postcode']
                    ))
                in_london = False
                for area_id, area in req.json()['areas'].items():
                    if area['type'] == "LBW":
                        in_london = True
                if not in_london:
                    return redirect('/map/?postcode_error={}&error={}'.format(
                        request.GET['postcode'],
                        "That postcode isn't in London"
                    ))

                y = req.json()['wgs84_lat']
                x = req.json()['wgs84_lon']


                return redirect('/map/?x={}&y={}'.format(x,y))
            except:
                return redirect('/map/?error={}'.format(
                    "Postcode not found"
                ))

        return super().get(request, *args, **kwargs)


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
