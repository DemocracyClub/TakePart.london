import re
import time

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
    url = "http://mapit.democracyclub.org.uk/postcode/{}".format(postcode)
    req = requests.get(url, headers={'User-Agent': 'scraper/sym', })
    mapit_data = req.json()
    ERROR_CODES = [404, 400]
    if mapit_data.get('code') in ERROR_CODES:
        if mapit_data.get('code') == 404:
            url = "https://mapit.mysociety.org/postcode/{}".format(postcode)
            req = requests.get(url)
            mapit_data = req.json()
            time.sleep(5)
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
        ))

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
                       mapit_url='http://mapit.democracyclub.org.uk',
                       sleep=0, try_more=True):
    req = requests.get(
        '{}/area/{}.wkt'.format(
            mapit_url,
            area_id,
            ), headers={'User-Agent': 'scraper/sym', })
    if sleep:
        time.sleep(sleep)
    print(req.status_code)
    if req.status_code == 200:
        area = req.text
        if area.startswith('POLYGON'):
            area = area[7:]
            area = "MULTIPOLYGON(%s)" % area
        return GEOSGeometry(area, srid=27700)
    elif req.status_code == 404:
        if try_more:
            print("Trying a different MaPit")
            time.sleep(10)
            return get_wkt_from_mapit(
                area_id,
                mapit_url="http://mapit.mysociety.org/",
                sleep=3, try_more=False)



# SELECT area, gss, name, population, population_voting_age, population_young, ward_id, borough_id, voters.count, ROUND(100.0 * count / population_voting_age) percent
# FROM register_ward
# INNER JOIN (
# SELECT ward_id, COUNT(address_hash) as count
# FROM register_registeredperson group by ward_id
# ) as voters
# ON register_ward.id=voters.ward_id
# --WHERE register_ward.borough_id=134
# ORDER BY percent DESC
