from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Updates the default site domain and name.'

    def handle(self, *args, **kwargs):
        try:
            site = Site.objects.get(pk=1)
            site.domain = 'localhost:8000'
            site.name = 'NutriTienda Local'
            site.save()
            self.stdout.write(self.style.SUCCESS("Successfully updated Site ID 1 to 'localhost:8000'"))
        except Site.DoesNotExist:
            self.stderr.write(self.style.ERROR("Site with ID 1 does not exist. Please check your database."))
