import csv
import sys

import ogr
import osr

LONDON_BOUNDS = {
    'min_lat': 51.28676016315085,
    'max_lat': 51.691874116909894,
    'max_lon': 0.3340155643740321,
    'min_lon': -0.5103750689005356,
}

DATA_ROOT = "../data/"
WKT = open('../data/london.wkt').read()
SHAPE = ogr.CreateGeometryFromWkt(WKT)

photos_tsv = open('{}images.csv'.format(
    DATA_ROOT
))

def lat_lng_in_bounds(lat, lon, bounds):
    in_london_lat = False
    in_london_lon = False

    lower_than_london_top = lat < bounds['max_lat']
    higher_than_london_bottom = lat > bounds['min_lat']
    in_london_lat = all((lower_than_london_top, higher_than_london_bottom))

    east_of_london_west = lon > bounds['min_lon']
    west_of_london_east = lon < bounds['max_lon']
    in_london_lon = all((east_of_london_west, west_of_london_east))

    if all((in_london_lon, in_london_lat)):
        return True

def lat_lng_in_shape(lat, lon, shape):
    point = ogr.Geometry(ogr.wkbPoint)
    point.AddPoint(lon, lat)

    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(4326)

    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(27700)

    coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    point.Transform(coordTransform)

    return shape.Contains(point)


all_photos =  csv.DictReader(photos_tsv)
out_file = csv.DictWriter(sys.stdout, fieldnames=all_photos.fieldnames)
out_file.writeheader()

for line in all_photos:
    if not line['wgs84_lat']:
        continue
    try:
        lat = float(line['wgs84_lat'])
        lon = float(line['wgs84_long'])
    except:
        continue
    if lat_lng_in_bounds(lat, lon, LONDON_BOUNDS):
        if lat_lng_in_shape(lat, lon, SHAPE):
            out_file.writerow(line)
