import json
from pathlib import Path

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Fills the DB with json-files with ingredients'

    def handle(self, *args, **kwargs):
        with open(Path('data', 'ingredients.json'), encoding='utf-8') as f:
            reader = json.load(f)
            ingredients, counter = [], 0
            for product in reader:
                ingredients.append(Ingredient(**product))
                counter += 1
            Ingredient.objects.bulk_create(ingredients, ignore_conflicts=True)
