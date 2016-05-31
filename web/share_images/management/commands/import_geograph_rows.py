import csv
import time

from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point, GEOSGeometry

from share_images.models import GeographImage


class Command(BaseCommand):
    def handle(self, **options):
        images_file = open('../data/images_in_london_and_son.csv')
        for line in csv.DictReader(images_file):
            location = Point(
                float(line['wgs84_long']),
                float(line['wgs84_lat'])
            )

            image_obj = GeographImage.objects.get_or_create(
                location=location,
                image_id=float(line['gridimage_id']),
                SON_AVG=float(line['SON_AVG']),
            )
