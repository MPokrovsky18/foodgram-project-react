from django.conf import settings
from django.db import models

MAX_CHARFIELD_LENGTH = 200
MAX_COLOR_CHARFIELD_LENGTH = 7
MAX_SLUGFIELD_LENGTH = 200

User = settings.AUTH_USER_MODEL


class Tag(models.Model):
    name = models.CharField(
        'Название', unique=True, max_length=MAX_CHARFIELD_LENGTH
    )
    color = models.CharField(
        'Цвет', unique=True, max_length=MAX_COLOR_CHARFIELD_LENGTH
    )
    slug = models.SlugField(
        'Слаг', unique=True, max_length=MAX_SLUGFIELD_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Название', unique=True, max_length=MAX_CHARFIELD_LENGTH
    )
    measurement_unit = models.CharField(
        'Единицы измерения', max_length=MAX_CHARFIELD_LENGTH
    )
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}/{self.measurement_unit}'

    def to_archive(self):
        self.is_archived = True
        self.save()
        ArchivedIngredient.objects.create(
            ingredient=self
        )

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if RecipeIngredient.objects.filter(ingredient=self).exists():
            self.to_archive()
        else:
            self.hard_delete(*args, **kwargs)


class ArchivedIngredient(models.Model):
    ingredient = models.OneToOneField(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='archive_data',
        verbose_name='Ингредиент'
    )
    archived_at = models.DateTimeField('Архивировано', auto_now_add=True,)

    class Meta:
        ordering = ('ingredient__name',)
        verbose_name = 'архивированный ингредиент'
        verbose_name_plural = 'Архивированные ингредиенты'

    def __str__(self) -> str:
        return str(self.ingredient)

    def unarchive(self):
        self.ingredient.is_archived = False
        self.ingredient.save()
        self.delete()

    def delete(self, *args, **kwargs):
        if self.ingredient.is_archived:
            self.ingredient.hard_delete()

        super().delete(*args, **kwargs)


class Recipe(models.Model):
    name = models.CharField('Название', max_length=MAX_CHARFIELD_LENGTH)
    image = models.ImageField('Изображение', blank=True, null=True)
    text = models.TextField('Описание')
    coocking_time = models.IntegerField('Время приготовления')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Опубликовано',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        null=True,
        on_delete=models.CASCADE
    )
    quantity = models.FloatField('Количество')
