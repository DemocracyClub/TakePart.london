import csv
import re
import time
import subprocess

import requests

from django.contrib.gis.geos import Point, GEOSGeometry
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.management.base import BaseCommand

from register.models import Ward
from share_images.models import ShareImage
from share_images.views import closest_image



class Command(BaseCommand):

    def make_image(self, ward):
        meme_url = "http://localhost:8000/share/{}".format(
            ward.gss
        )

        img_temp = NamedTemporaryFile(delete=True)
        subprocess.call(
            'phantomjs capture.js {} {}'.format(
                ward.gss,
                meme_url
                ),
            shell=True)
        shareimage = ShareImage.objects.create(ward=ward)
        shareimage.save()

        with open("/tmp/{}.png".format(ward.gss), 'rb') as image_file:
            shareimage.image.save('{}.jpg'.format(ward.gss), File(image_file))

        shareimage.save()
        ward.shareimage = shareimage
        ward.save()

    def handle(self, **options):
        for ward in Ward.objects.filter(shareimage=None):
            self.make_image(ward)
