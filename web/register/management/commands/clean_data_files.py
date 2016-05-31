import codecs
import os
import csv
import glob
import hashlib

from django.core.management.base import BaseCommand


class PostcodeError(Exception):
    pass


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--gss',
        dest='gss',
        default='*',
        help='borough gss')

    def handle(self, *args, **options):
        files_this_run = set()
        for csv_path in glob.glob('../data/electoral_rolls/{}*/*.csv'.format(
            options['gss']
        )):
            file_name = csv_path.split('/')[-1]
            if file_name == "cleaned.csv":
                continue
            print(csv_path)

            gss = csv_path.split('/')[-2].split('-')[0]
            dir_name = os.path.dirname(csv_path)

            if gss in files_this_run:
                out_csv = csv.writer(open("{}/cleaned.csv".format(dir_name), 'a'))
            else:
                out_csv = csv.writer(open("{}/cleaned.csv".format(dir_name), 'w'))
                files_this_run.add(gss)
            # pk = 1

            for line in self.clean_csv(csv_path):
                if line[0] and line[1] and line[2]:
                    line.append(gss)
                    out_csv.writerow(line)
                    # pk += 1

    def open_csv(self, csv_path):
        data = codecs.open(csv_path, 'r', 'latin-1')
        reader = csv.DictReader(
            data, delimiter="\t", restkey="extra_", restval="foo")
        if len(reader.fieldnames) == 1:
            data.seek(0)
            reader = csv.DictReader(
                data, delimiter=",", restkey="extra_", restval="foo")
        return reader

    def is_postcode_match(self, postcode_guess):
        import re
        return re.match(
            r"[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][ABD-HJLNP-UW-Z]{2}",
            postcode_guess)

    def get_postcode_from_line(self, line):
        field_name_attempts = [
            'PostCode',
            'Post Code',
            'Postcode',
            'PropertyPostCode',
        ]
        for field_name in field_name_attempts:
            if field_name in line:
                if not self.is_postcode_match(line[field_name]):
                    for k,v in line.items():
                        if self.is_postcode_match(v):
                            return v
                return line[field_name]
        raise ValueError("unknown postcode field")

    def get_address_from_line(self, line):
        address_names = [
            ['Address 1', 'Address1', 'RegisteredAddress1', 'PropertyAddress1', 'address1',],
            ['Address 2', 'Address2', 'RegisteredAddress2', 'PropertyAddress2', 'address2',],
            ['Address 3', 'Address3', 'RegisteredAddress3', 'PropertyAddress3',],
            ['Address 4', 'Address4', 'RegisteredAddress4', 'PropertyAddress4',],
            ['Address 5', 'Address5', 'RegisteredAddress5', 'PropertyAddress5',],
            ['Address 6', 'Address6', 'RegisteredAddress6',],
        ]
        address = []
        for address_name in address_names:
            for name in address_name:
                if name in line:
                    address.append(line[name])

        address = ", ".join([line.strip() for line in address if line])
        address = address.replace('\n', ', ')
        return address

    def get_line_hash(self, line):
        line_str = "--".join([str(x) for x in line.values() if x]).encode('utf8')
        return hashlib.sha224(line_str).hexdigest()

    def clean_csv(self, csv_path):
        for line in self.open_csv(csv_path):
            try:
                postcode = self.get_postcode_from_line(line)
            except ValueError:
                print(line)
                import sys
                sys.exit(1)
            yield [
                self.get_line_hash(line),
                postcode,
                self.get_address_from_line(line),
            ]

