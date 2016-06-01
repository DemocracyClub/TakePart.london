import csv
import re
import time

import requests

from django.contrib.gis.geos import Point, GEOSGeometry
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.management.base import BaseCommand

from share_images.models import GeographImage


class Command(BaseCommand):

    def get_image(self, image):
        deepdream_url = "http://52.29.134.217/final/{}.jpg".format(
            image.pk
        )
        req = requests.get(deepdream_url)
        if req.status_code != 200:
            return

        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(req.content)
        img_temp.flush()

        image.dream_image.save('{}.jpg'.format(image.pk), File(img_temp))

        image.save()

    def handle(self, **options):
        images = GeographImage.objects.filter(dream_image='')
        for image in images:
            self.get_image(image)
