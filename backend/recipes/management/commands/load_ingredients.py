import json

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов в базу данных из JSON-файла'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file_path',
            type=str,
            help='Путь к JSON-файлу',
        )
        parser.add_argument(
            '--batch_size',
            type=int,
            default=100,
            help='Размер пакета для пакетной вставки',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить базу данных перед загрузкой ингредиентов',
        )

    def handle(self, *args, **options):
        json_file_path = options.get('json_file_path')
        batch_size = options.get('batch_size')
        clear_database = options.get('clear')

        if not json_file_path:
            raise CommandError(
                'Не указан обязательный аргумент json_file_path. '
                'Укажите путь к JSON-файлу.'
            )

        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

                if clear_database:
                    Ingredient.objects.all().delete()

                start_ingredients_count = Ingredient.objects.count()
                loaded_ingredients = []

                for item in data:
                    loaded_ingredients.append(
                        Ingredient(
                            name=item['name'],
                            measurement_unit=item['measurement_unit']
                        )
                    )

                    if len(loaded_ingredients) >= batch_size:
                        Ingredient.objects.bulk_create(
                            loaded_ingredients,
                            ignore_conflicts=True
                        )
                        loaded_ingredients = []

                if loaded_ingredients:
                    Ingredient.objects.bulk_create(
                        loaded_ingredients,
                        ignore_conflicts=True
                    )

            count_loaded = Ingredient.objects.count() - start_ingredients_count

            self.stdout.write(
                self.style.SUCCESS(
                    f'Загружено {count_loaded} ингредиентов!'
                )
            )
        except FileNotFoundError:
            raise CommandError(
                f'Файл "{json_file_path}" не найден. '
                'Проверьте путь, который указан к JSON-файлу.'
            )
        except json.JSONDecodeError:
            raise CommandError(
                f'Файл "{json_file_path}" содержит '
                'недопустимый синтаксис для JSON-файла.'
            )
