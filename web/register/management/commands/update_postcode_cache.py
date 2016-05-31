from django.db import connection
from django.core.management.base import BaseCommand


class PostcodeError(Exception):
    pass


class Command(BaseCommand):
    def handle(self, **options):
        cursor = connection.cursor()

        cursor.execute("""
        INSERT INTO register_postcodecachedata (
        SELECT d.postcode, d.location as location, d.borough_gss, d.ward_gss
        FROM
        (
            SELECT DISTINCT ON (postcode) postcode,
                   borough_gss, rw.gss ward_gss, location
            FROM register_registeredperson
            JOIN register_ward rw
            ON ward_id=rw.id
            WHERE location IS NOT NULL
            GROUP BY postcode, borough_gss, ward_gss, location
        ) as d
        LEFT JOIN register_postcodecachedata as pcd
        ON d.postcode=pcd.postcode
        WHERE d.location IS NOT NULL
        AND pcd.postcode IS NULL
        GROUP BY d.postcode,
                d.ward_gss, d.borough_gss, d.location

        )
        """)
