import csv

SON_DATA = open('../data/scenicornot_votes.tsv')
SON_CSV = csv.DictReader(SON_DATA, delimiter='\t')
SON_DICT = {}

for line in SON_CSV:
    gg_id = str(line['Geograph URI'].split('/')[-1])
    SON_DICT[gg_id] = line['Average']


IMAGES_FILE = open('../data/images_in_london.csv')
IMAGES_CSV = csv.DictReader(IMAGES_FILE)

fieldnames = IMAGES_CSV.fieldnames
fieldnames.append('SON_AVG')

OUT_FILE = open('../data/images_in_london_and_son.csv', 'w')
OUT_CSV = csv.DictWriter(OUT_FILE, fieldnames=IMAGES_CSV.fieldnames)
for line in IMAGES_CSV:
    print(line['gridimage_id'] in SON_DICT)
    line['SON_AVG'] = SON_DICT.get(line['gridimage_id'], 5)

    OUT_CSV.writerow(line)
