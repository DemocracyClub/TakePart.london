from __future__ import absolute_import

from django.db import transaction

from celery import shared_task

from register.utils import geocode_postcode


@shared_task
def geocode_task(postcode):
    geocode_postcode(postcode)
