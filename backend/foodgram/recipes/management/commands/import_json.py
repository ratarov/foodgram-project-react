import json
from pathlib import Path

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Fills the DB with json-files with ingredients'

    def handle(self, *args, **kwargs):
        mapping = (
            ('ingredients.json', Ingredient),
            ('tags.json', Tag)
        )
        for file, model in mapping:
            self.stdout.write(f'Начинаем импорт из файла {file}')
            with open(Path('data', file), encoding='utf-8') as f:
                reader = json.load(f)
                items, counter = [], 0
                for attrs in reader:
                    items.append(model(**attrs))
                    counter += 1
                model.objects.bulk_create(items, ignore_conflicts=True)
                self.stdout.write(
                    f'Добавлено объектов: {len(reader)}; '
                    f'строк в документе: {counter}\n'
                    '-------------------------------------------------')
