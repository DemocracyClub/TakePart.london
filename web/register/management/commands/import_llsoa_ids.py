import time

from django.core.management.base import BaseCommand

import requests

from register.models import Borough, LLSOA


class PostcodeError(Exception):
    pass


class Command(BaseCommand):
    postcode_cache = {}

    def process_borough(self, borough):
        req = requests.get(
            'http://mapit.mysociety.org/area/{}'.format(
                borough.gss,
            ))
        url = req.url
        req = requests.get("{}/coverlaps?type=OLF".format(url))
        for area_id, area_data in req.json().items():
            LLSOA.objects.get_or_create(
                gss=area_data['codes']['ons'],
                defaults={
                    'name': area_data['name']
                })
        time.sleep(5)




    def handle(self, **options):
        for borough in Borough.objects.all():
            print(borough.name)
            self.process_borough(borough)
