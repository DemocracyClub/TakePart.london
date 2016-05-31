import csv
import sys

from register.utils import geocode_postcode

data_file = open('../data/electoral_rolls/Lambeth.csv')

register = csv.DictReader(data_file)
fieldnames = register.fieldnames
fieldnames = fieldnames + ['ward_name', 'ward_gss', 'lat', 'lon', ]
out_file = csv.DictWriter(sys.stdout, fieldnames=fieldnames)

out_file.writeheader()
for line in register:
    line.update(geocode_postcode(line['PostCode']))
    out_file.writerow(line)
