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

    def handle(self, **options):
        for ward in Ward.objects.exclude(shareimage=None):
            token = "EAACEdEose0cBAJh2SsiGnBOZBkUb5GQfOZCzLhdtwEMfXM3v4IKXDctY69NrZBFfc0V4J3QQuDZCuszYsWqzBCGZCKCDZCNIdPtNJ5hLKvZBeUXDsFZCFgenL8ziHurapIbYONP5sTQkEEuIqZBnrf2MEJjffcymShYXzwzv0aZBp3GQZDZD"
            cmd = """curl -i -X POST -d "scrape=true" -d "id=http%3A%2F%2Ftakepart.london%2Fward%2F{}" -d "access_token={}" "https://graph.facebook.com/v2.6/" """.format(
                ward.gss,
                token,
            )
            print(cmd)
            subprocess.call(cmd, shell=True)
