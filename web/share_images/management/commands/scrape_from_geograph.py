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
        reuse_url = "http://www.geograph.org.uk/reuse.php?id={}".format(
            image.pk
        )
        req = requests.get(reuse_url)
        image_hash = re.search(
            r'reuse.php\?id={}&amp;download=([^"]+)'.format(image.pk),
            req.text).group(1)

        time.sleep(1)

        req = requests.get("{}&amp;download={}".format(
            reuse_url,
            image_hash
            ))

        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(req.content)
        img_temp.flush()

        image.orig_image.save('{}.jpg'.format(image.pk), File(img_temp))

        image.save()
        time.sleep(1)

    def handle(self, **options):
        images = GeographImage.objects.filter(orig_image=None)
        for image in images:
            self.get_image(image)




