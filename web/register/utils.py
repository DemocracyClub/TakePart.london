import re
import time

from django.conf import settings
from django.contrib.gis.geos import Point, GEOSGeometry

import requests

from register.models import RegisteredPerson, Ward, Borough


class PostcodeError(Exception):
    pass


def _geocode_postcode(postcode):
    if not postcode:
        raise PostcodeError
    if not re.match(r"^[A-Za-z]+[0-9]", postcode):
        raise PostcodeError
    data = {}
    url = "http://mapit.mysociety.org/postcode/{}".format(postcode)
    req = requests.get(url, headers=settings.MAPIT_HEADERS)
    mapit_data = req.json()
    ERROR_CODES = [404, 400]
    if mapit_data.get('code') in ERROR_CODES:
        raise PostcodeError

    data['lat'] = mapit_data['wgs84_lat']
    data['lon'] = mapit_data['wgs84_lon']
    return data


def get_postcode_qs(postcode):
    return RegisteredPerson.objects.filter(
        postcode=postcode).exclude(postcode_error=True)


def get_areas_from_postcode(postcode, areas=None):
    if not areas:
        areas = ['LBO', 'LBW']
    data = {}
    req = requests.get(
        "http://mapit.mysociety.org/postcode/{}?generation=21".format(
            postcode
        ), headers=settings.MAPIT_HEADERS)

    for area_id, area in req.json()['areas'].items():
        if area['type'] in areas:
            data[area['type']] = area
    time.sleep(3)
    return data


def geocode_postcode(postcode):
    kwargs = {}
    addresses = get_postcode_qs(postcode)
    if not addresses:
        return
    if not addresses.first().location:
        try:
            data = _geocode_postcode(postcode)
        except PostcodeError:
            addresses.update(postcode_error=True)
            return
        kwargs['location'] = Point(data['lon'], data['lat'])
    else:
        kwargs['location'] = addresses.first().location

    try:
        ward = Ward.objects.get(area__covers=kwargs['location'])
        borough = ward.borough
    except Ward.DoesNotExist:
        data = get_areas_from_postcode(postcode)
        if 'LBO' in data:
            borough, _ = Borough.objects.get_or_create(
                gss=data['LBO']['codes']['gss'],
                name=data['LBO']['name']
            )
            borough.area = get_wkt_from_mapit(borough.gss)
            borough.save()
        if 'LBW' in data:
            ward, _ = Ward.objects.get_or_create(
                gss=data['LBW']['codes']['gss'],
                name=data['LBW']['name'],
                borough=borough
            )
            if not ward.area:
                area = get_wkt_from_mapit(ward.gss)
                if area:
                    ward.area = area
            ward.save()
        else:
            return addresses.update(postcode_error=True)

    kwargs['ward'] = ward
    kwargs['borough'] = borough

    addresses.update(**kwargs)


def get_wkt_from_mapit(area_id,
                       mapit_url='http://mapit.mysociety.org/',
                       sleep=0):
    req = requests.get(
        '{}/area/{}.wkt'.format(
            mapit_url,
            area_id,
            ), headers=settings.MAPIT_HEADERS)
    if sleep:
        time.sleep(sleep)
    print(req.status_code)
    if req.status_code == 200:
        area = req.text
        if area.startswith('POLYGON'):
            area = area[7:]
            area = "MULTIPOLYGON(%s)" % area
        return GEOSGeometry(area, srid=27700)



# SELECT area, gss, name, population, population_voting_age, population_young, ward_id, borough_id, voters.count, ROUND(100.0 * count / population_voting_age) percent
# FROM register_ward
# INNER JOIN (
# SELECT ward_id, COUNT(address_hash) as count
# FROM register_registeredperson group by ward_id
# ) as voters
# ON register_ward.id=voters.ward_id
# --WHERE register_ward.borough_id=134
# ORDER BY percent DESC
