import json
from pathlib import Path

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    help = 'Fills the DB with fixtures'

    def handle(self, *args, **kwargs):
        mapping = (
            ('ingredients.json', Ingredient),
            ('tags.json', Tag)
        )
        for file, model in mapping:
            self.stdout.write(f'Начинаем импорт из файла {file}')
            try:
                with open(Path('data', file), encoding='utf-8') as f:
                    reader = json.load(f)
            except FileNotFoundError:
                self.stderr.write(
                    f'File {file} не найден\n'
                    '-------------------------------------------------')
                continue    
            items, counter = [], 0
            for attrs in reader:
                try:
                    items.append(model(**attrs))
                    counter += 1
                except TypeError:
                    self.stderr.write(f'Ошибка в заполнении фикстур')
                    continue
            model.objects.bulk_create(items, ignore_conflicts=True)
            self.stdout.write(
                f'Добавлено объектов: {len(reader)}; '
                f'строк в документе: {counter}\n'
                '-------------------------------------------------')
