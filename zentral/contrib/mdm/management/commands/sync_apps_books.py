from django.core.management.base import BaseCommand
from zentral.contrib.mdm.models import Location
from zentral.contrib.mdm.apps_books import sync_assets
from zentral.core.queues import queues


class Command(BaseCommand):
    help = 'Sync apps & books locations assets'

    def add_arguments(self, parser):
        parser.add_argument('--list-locations', action='store_true', dest='list_locations', default=False,
                            help='list existing apps & books locations')
        parser.add_argument('--location', dest='location_ids', type=int, nargs=1,
                            help='sync apps & books locations assets')

    def write(self, msg):
        if self.verbosity:
            self.stdout.write(msg)

    def handle(self, *args, **kwargs):
        self.verbosity = kwargs.get("verbosity", 1)
        location_qs = Location.objects.all().order_by("name")
        if kwargs.get('list_locations'):
            self.write("Existing locations:")
            for location in location_qs:
                self.write(f"{location.pk} {location}")
            return
        location_ids = kwargs.get("location_ids")
        if location_ids:
            location_qs = location_qs.filter(pk__in=location_ids)
        for location in location_qs:
            self.write(f"Sync apps & books for location {location.pk} {location}")
            sync_assets(location)
        queues.stop()
