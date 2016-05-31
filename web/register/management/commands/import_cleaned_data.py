import csv
import glob
import os

from django.core.management import call_command
from django.db import connection
from django.core.management.base import BaseCommand
from django.db import transaction

from register.models import RegisteredPerson

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--gss',
        dest='gss',
        default='*',
        help='borough gss')


    def handle(self, **options):
        data_files = glob.glob('../data/electoral_rolls/{}*/cleaned.csv'.format(
            options['gss']
        ))
        for csv_path in data_files:
            print(csv_path)
            gss = csv_path.split('/')[-2].split('-')[0]

            cursor = connection.cursor()
            # call_command('update_postcode_cache', interactive=True)

            cursor.execute("""
            SELECT COUNT(*)
            FROM register_registeredperson
            WHERE borough_gss='{}'
            """.format(gss))
            count = cursor.fetchone()[0]
            # if count:
            #     continue

            cursor.execute("""
                DELETE FROM register_registeredperson
                WHERE borough_gss='{}'
            """.format(gss))

            cursor.execute("""
                COPY register_registeredperson (address_hash,postcode,address,borough_gss)
                FROM '{}' (FORMAT CSV, DELIMITER ',', quote '"');
            """.format(os.path.abspath(csv_path)))


            # cursor.execute("""
            # UPDATE register_registeredperson rp
            # SET location=sq.location, ward_id=sq.ward_id, borough_id=sq.borough_id
            # FROM (
            #     SELECT pcd.postcode, pcd.id, rw.id, pcd.location
            #     FROM (
            #         SELECT pcd.postcode, pcd.id, rw.gss as gss FROM (
            #             SELECT pcd.postcode, rb.id
            #             FROM register_postcodecachedata pcd
            #             JOIN register_borough as rb
            #             ON rb.gss=pcd.borough_gss
            #         ) as rw
            #         JOIN register_ward
            #         ON rw.gss=pcd.ward_gss
            #     ) as pcd
            #     JOIN register_registeredperson as d
            #     ON d.postcode=pcd.postcode
            # ) as sq
            # WHERE rp.postcode=sq.postcode
            # AND borough_gss='{}'
            # """.format(gss))


        # existing_ids = set([
        #     r
        #     for r in
        #     RegisteredPerson.objects.values_list('address_hash', flat=True)])
        # print("I know about {} addresses already".format(
        #     len(existing_ids)
        # ))
        # # with transaction.atomic():
        # for line in csv.reader(data_file):
        #     address_hash, postcode, address = line
        #     if address_hash in existing_ids:
        #         continue
        #     RegisteredPerson.objects.create(
        #         address_hash=address_hash,
        #         address = address,
        #         postcode = postcode,
        #     )
