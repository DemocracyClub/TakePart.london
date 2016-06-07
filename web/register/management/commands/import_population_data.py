import csv
from collections import defaultdict
from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection

from register.models import Ward, LLSOA, Borough, RegisteredPerson


class PostcodeError(Exception):
    pass


class Command(BaseCommand):

    def population_count_by_age_range(self, young, old, line):
        age_counter = []
        for i in range(young, old):
            age_count = line.get(str(i), '0')
            age_count = age_count.replace(',', '')
            age_counter.append(int(age_count))
        return sum(age_counter)

    # def import_2014_data(self):
    #     population_cache = {}
    #     population_data_file = open('../data/populations.csv')
    #     for line in csv.DictReader(population_data_file):
    #         line['young_count'] = self.population_count_by_age_range(
    #             18, 25, line)
    #         line['adult_count'] = self.population_count_by_age_range(
    #             18, 120, line)
    #         population_cache[line['Ward Code 1']] = line
    #
    #     for ward in Ward.objects.all():
    #         if ward.gss in population_cache.keys():
    #             data = population_cache[ward.gss]
    #             ward.population_young = data['young_count']
    #             ward.population_voting_age = data['adult_count']
    #             ward.population = data['All Ages'].replace(',', '')
    #             ward.save()

    def import_gla_data(self):
        population_data_file = open('../data/populations_gla.csv')
        print("Iterating over lines in GLA populations file")
        for line in csv.DictReader(population_data_file):
            gss = line['GSS.Code.Ward']
            data = self.ward_data[gss]

            for year in (self.year, self.baseline_year):
                if year not in data:
                    data[year] = {}
                # always update the total population
                population = data[year].get('All Ages', 0)
                population += int(line[year])
                data[year]['All Ages'] = population

                if int(line['Age']) in self.young_person:
                    young_population = data[year].get('young_count', 0)
                    young_population += int(line[year])
                    data[year]['young_count'] = young_population

                if int(line['Age']) >= self.voting_age:
                    voting_population = data[year].get('adult_count', 0)
                    voting_population += int(line[year])
                    data[year]['adult_count'] = voting_population

                assert data[year].get('adult_count', 0) >= \
                    data[year].get('young_count', 0)

        for gss, data in self.ward_data.items():
            try:
                ward = Ward.objects.get(
                    gss=gss
                )
            except Ward.DoesNotExist:
                print("{} not found".format(gss))
                continue

            ward.growth_rate = (
                (data[self.year]['All Ages'] - \
                 data[self.baseline_year]['All Ages'])
                 / data[self.baseline_year]['All Ages'])

            ward.population_young = data[self.year]['young_count']
            ward.population_voting_age = data[self.year]['adult_count']
            ward.population = data[self.year]['All Ages']

            ward.save()


    def import_llsoa_data(self):
        def grow(x, y):
            x = float(x)
            return  + int(x + (x * y))

        population_data_file = open('../data/llsoa_populations_2014.csv')
        for line in csv.DictReader(population_data_file):
            line['young_count'] = self.population_count_by_age_range(
                18, 25, line)
            line['adult_count'] = self.population_count_by_age_range(
                18, 120, line)
            self.llsoa_data[line['Area Codes']] = line

        for llsoa in LLSOA.objects.all():
            if llsoa.gss in self.llsoa_data.keys():
                data = self.llsoa_data[llsoa.gss]
                llsoa.population_young_2014 = data['young_count']
                llsoa.population_voting_age_2014 = data['adult_count']
                llsoa.population_2014 = data['All Ages'].replace(',', '')
                llsoa.ward = Ward.objects.filter(
                    area__covers=llsoa.area.centroid).first()
                if not llsoa.ward:
                    llsoa.ward = Ward.objects.filter(
                        area__overlaps=llsoa.area).first()

                llsoa.save()

                if not llsoa.ward:
                    continue
                ward_gss = llsoa.ward.gss
                if ward_gss in self.growth_ratios:
                    llsoa.growth_rate = Decimal(float(self.growth_ratios[ward_gss]))
                    llsoa.population_young = grow(
                        data['young_count'], self.growth_ratios[ward_gss]
                    )

                    llsoa.population_voting_age = grow(
                        data['adult_count'], self.growth_ratios[ward_gss]
                    )
                    llsoa.population = grow(
                        llsoa.population_2014, self.growth_ratios[ward_gss]
                    )
                    llsoa.save()


    def fixes(self):
        ward = Ward.objects.get(gss="E05000557")
        ward.registered_count = 7135
        ward.percent_registered= 86
        ward.save()

        ward = Ward.objects.get(gss="E05000556")
        ward.registered_count = 7950
        ward.percent_registered= 86
        ward.save()

        def fix_max_percent(object_type):
            for area in object_type.objects.all():
                if area.percent_registered and area.percent_registered > 99:
                    area.percent_registered = 99
                    area.save()
        print('Fixing wards')
        fix_max_percent(Ward)
        print('Fixing LLSOAs')
        fix_max_percent(LLSOA)

    def make_growth_ratios(self):
        self.growth_ratios = {}
        for gss, years in self.ward_data.items():
            then_population = years[self.baseline_year]['All Ages']
            now_population = years[self.year]['All Ages']

            ratio = (now_population - then_population) / then_population
            self.growth_ratios[gss] = ratio

    def handle(self, **options):
        self.baseline_year = '2014'
        self.year = '2016'
        self.young_person = range(18, 25)
        self.voting_age = 18
        self.ward_data = defaultdict(dict)
        self.llsoa_data = defaultdict(dict)

        print('Importing GLA data')
        # self.import_gla_data()
        # # call_command('add_geom_to_areas', interactive=True)
        # print('Making growth rates')
        # self.make_growth_ratios()
        # print('Importing LLSOA data')
        # self.import_llsoa_data()
        print('Updating DB caches')
        self.update_db_caches()
        print('Fixing!')
        self.fixes()

    def update_db_caches(self):
        print("Updating cache for ward_ids")
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE register_ward
            SET
                registered_count=d.registered_count,
                percent_registered=d.percent
            FROM (
                SELECT
                    gss, name, population, population_voting_age,
                    population_young, ward_id, borough_id, voters.count
                    registered_count,
                    ROUND(100.0 * count / population_voting_age) percent
                FROM register_ward
                INNER JOIN (
                    SELECT ward_id, COUNT(address_hash) as count
                    FROM register_registeredperson group by ward_id
                ) as voters
                ON register_ward.id=voters.ward_id
                ORDER BY percent DESC
            ) as d
            WHERE register_ward.gss=d.gss
        """)

        print("Updating cache for LLSOAs")
        for llsoa in LLSOA.objects.all():
            llsoa.registered_count = RegisteredPerson.objects.filter(
                location__within=llsoa.area).count()
            if llsoa.registered_count and llsoa.population_voting_age:
                llsoa.percent_registered = 100 * llsoa.registered_count / llsoa.population_voting_age
            llsoa.save()



# SELECT area, gss, name, population, population_voting_age, population_young, ward_id, borough_id, voters.count, ROUND(100.0 * count / population_voting_age) percent
# FROM register_ward
# INNER JOIN (
# SELECT ward_id, COUNT(address_hash) as count
# FROM register_registeredperson group by ward_id
# ) as voters
# ON register_ward.id=voters.ward_id
# WHERE register_ward.borough_id=4
# ORDER BY percent DESC
