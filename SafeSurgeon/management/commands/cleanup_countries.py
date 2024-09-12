# Create a new file: SafeSurgeon/management/commands/cleanup_countries.py

from django.core.management.base import BaseCommand
from SafeSurgeon.models import Country, City

class Command(BaseCommand):
    help = 'Cleans up duplicate country entries and associated cities'

    def handle(self, *args, **options):
        # Find all countries named 'Default Country'
        default_countries = Country.objects.filter(name='Default Country')
        
        if default_countries.count() > 1:
            # Keep the first one and delete the rest
            primary_country = default_countries.first()
            for country in default_countries[1:]:
                # Update cities to point to the primary country
                City.objects.filter(country=country).update(country=primary_country)
                country.delete()
            
            self.stdout.write(self.style.SUCCESS(f'Cleaned up duplicate Default Country entries. Kept ID: {primary_country.id}'))
        else:
            self.stdout.write(self.style.SUCCESS('No duplicate Default Country entries found.'))

        # Optional: List all countries
        self.stdout.write("Current countries in the database:")
        for country in Country.objects.all():
            self.stdout.write(f"- {country.name} (ID: {country.id})")