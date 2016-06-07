import csv
import time

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point, GEOSGeometry

import requests

from register.models import RegisteredPerson, Ward, Borough, LLSOA
from register.utils import get_wkt_from_mapit

class PostcodeError(Exception):
    pass

class Command(BaseCommand):
    postcode_cache = {}


    def process_qs(self, qs, **kwargs):
        for area in qs:
            print(area.name, area.gss)
            geom = get_wkt_from_mapit(area.gss, **kwargs)
            if geom:
                area.area = geom
                area.save()
            else:
                print("Error")
                time.sleep(30)


    def handle(self, **options):
        print("Adding areas to wards")
        self.process_qs(Ward.objects.filter(area=None))
        print("Adding areas to boroughs")
        self.process_qs(Borough.objects.filter(area=None))
        print("Adding areas to LLSOAs")
        self.process_qs(
            LLSOA.objects.filter(area=None),
            mapit_url="http://mapit.mysociety.org/",
            sleep=3
        )

