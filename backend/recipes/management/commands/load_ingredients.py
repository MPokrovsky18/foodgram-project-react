import json

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient, Tag

PATH_TO_INGREDIENTS = './data/ingredients.json'
PATH_TO_TAGS = './data/tags.json'


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            for path, type in (
                (PATH_TO_INGREDIENTS, Ingredient),
                (PATH_TO_TAGS, Tag)
            ):
                self.load_to_db(path, type)

            self.stdout.write(
                self.style.SUCCESS('Данные загружены!')
            )
        except Exception as exc:
            raise CommandError(exc)

    def load_to_db(self, path, type):
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)

            for item in data:
                type.objects.get_or_create(**item)
