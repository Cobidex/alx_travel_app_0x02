import random
from django.core.management.base import BaseCommand
from listings.models import Listing  # Ensure you import the correct model

class Command(BaseCommand):
    help = "Seeds the database with sample listings data"

    def handle(self, *args, **kwargs):
        sample_data = [
            {
                "property_id": "1",
                "host_id": "1",
                "name": "Luxury Villa",
                "description": "A beautiful villa with a pool",
                "location": "Los Angeles",
                "pricepernight": 500,
            },
            {
                "property_id": "2",
                "host_id": "2",
                "name": "Beach House",
                "description": "A cozy beach house with a view",
                "location": "Miami",
                "pricepernight": 300,
            },
            {
                "property_id": "3",
                "host_id": "3",
                "name": "Mountain Cabin",
                "description": "A rustic cabin in the mountains",
                "location": "Aspen",
                "pricepernight": 200,
            },
        ]

        for data in sample_data:
            Listing.objects.create(**data)

        self.stdout.write(self.style.SUCCESS("Successfully seeded sample listings data!"))
