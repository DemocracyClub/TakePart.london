from django.core.management.base import BaseCommand
from django.core.management import call_command

from register.models import RegisteredPerson
from register.tasks import geocode_task



class Command(BaseCommand):
    seen_postcodes = set()

    def get_empty_qs(self):
        return RegisteredPerson.objects.filter(
            location=None
            ).exclude(postcode_error=True)

    def handle(self, **options):
        call_command('add_geom_to_areas', interactive=True)
        for address in self.get_empty_qs():
            postcode = address.postcode
            if postcode not in self.seen_postcodes:

                # from register.utils import geocode_postcode
                # geocode_postcode(postcode)

                geocode_task.delay(postcode)
                self.seen_postcodes.add(postcode)
