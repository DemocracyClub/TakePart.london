import os
import csv
import re
import time
import subprocess
import glob

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

    def clean_up_errors(self):
        for ward in Ward.objects.exclude(shareimage=None):
            image_path = ward.shareimage.image.path
            if not os.path.exists(image_path):
                ward.shareimage.delete()
                ward.save()

        for path in glob.glob('web/media/images/shares/*'):
            if os.path.getsize(path) < 50000:
                gss = path.split('/')[-1].split('.')[0]
                ward = Ward.objects.get(gss=gss)
                try:
                    ward.shareimage.delete()
                    ward.save()
                except:
                    pass
                os.remove(path)

    def handle(self, **options):
        self.clean_up_errors()
        print(Ward.objects.filter(shareimage=None).count())
        for ward in Ward.objects.filter(shareimage=None):
            self.make_image(ward)
