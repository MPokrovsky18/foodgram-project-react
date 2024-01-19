from django.conf import settings
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

User = settings.AUTH_USER_MODEL


class Tag(models.Model):
    name = models.CharField('Название', unique=True, max_length=200)
    color = models.CharField('Цвет', unique=True, max_length=7)
    slug = models.SlugField('Слаг', unique=True, max_length=200)

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField('Название', unique=True, max_length=200)
    measurement_unit = models.CharField(
        'Единицы измерения', unique=True, max_length=200
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class ArchivedIngredient(Ingredient):
    archived_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Архивировано',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'архивный ингредиент'
        verbose_name_plural = 'Архивные ингредиенты'


class Recipe(models.Model):
    name = models.CharField('Название', max_length=200)
    image = models.ImageField('Изображение')
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
        on_delete=models.CASCADE
    )
    quantity = models.FloatField('Количество')


@receiver(pre_delete, sender=Ingredient)
def archive_ingredient(sender, instance, **kwargs):
    if (
        not isinstance(instance, ArchivedIngredient)
        and RecipeIngredient.objects.filter(ingredient=instance).exists()
    ):
        archived_ingredient = ArchivedIngredient.objects.create(
            name=instance.name,
            measurement_unit=instance.measurement_unit,
        )

        RecipeIngredient.objects.filter(
            ingredient=instance
            ).update(
                ingredient=archived_ingredient
            )
