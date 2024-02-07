import json

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient, Tag

PATH_TO_INGREDIENTS = './data/ingredients.json'
PATH_TO_TAGS = './data/tags.json'


class Command(BaseCommand):
    """Custom management command to load data from JSON files."""

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

    @staticmethod
    def load_to_db(path, type):
        """Load data from a JSON file into the specified model."""
        with open(path, 'r', encoding='utf-8') as file:
            data = json.load(file)

            for item in data:
                type.objects.get_or_create(**item)
