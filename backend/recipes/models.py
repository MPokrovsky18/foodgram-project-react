from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from recipes import constants


class Tag(models.Model):
    name = models.CharField(
        'Название',
        unique=True,
        max_length=constants.MAX_TEXTFIELD_LENGTH
    )
    color = ColorField('Цвет', unique=True)
    slug = models.SlugField(
        'Слаг',
        unique=True,
        max_length=constants.MAX_TEXTFIELD_LENGTH,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name[:constants.MAX_STRING_LENGHT]


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=constants.MAX_TEXTFIELD_LENGTH
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=constants.MAX_TEXTFIELD_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit'
            ),
        )

    def __str__(self):
        return (
            f'{self.name[:constants.MAX_STRING_LENGHT]}'
            f'/{self.measurement_unit}'
        )


class Recipe(models.Model):
    name = models.CharField(
        'Название',
        max_length=constants.MAX_TEXTFIELD_LENGTH
    )
    image = models.ImageField('Изображение', upload_to='recipes/images/')
    text = models.TextField('Описание')
    cooking_time = models.SmallIntegerField(
        'Время приготовления',
        validators=(
            MinValueValidator(
                constants.MIN_VALUE,
                message=('Время приготовления '
                         f'не может быть меньше {constants.MIN_VALUE}.')
            ),
            MaxValueValidator(
                constants.MIN_VALUE,
                message=('Время приготовления '
                         f'не может быть больше {constants.MAX_VALUE}.')
            ),
        )
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Опубликовано',
    )
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name[:constants.MAX_STRING_LENGHT]


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.SmallIntegerField(
        'Количество',
        default=constants.MIN_VALUE,
        validators=(
            MinValueValidator(
                constants.MIN_VALUE,
                message=('Количество ингредиента '
                         f'не может быть меньше {constants.MIN_VALUE}.')
            ),
            MaxValueValidator(
                constants.MIN_VALUE,
                message=('Количество ингредиента '
                         f'не может быть больше {constants.MAX_VALUE}.')
            ),
        )
    )

    class Meta:
        default_related_name = 'ingredient_in_recipe'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            ),
        )
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self) -> str:
        return f'{self.ingredient} - {self.amount}'


class BaseFavourites(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True


class Favourites(BaseFavourites):
    class Meta:
        default_related_name = 'favourites'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_recipe_user_favourites'
            ),
        )


class ShoppingCart(BaseFavourites):
    class Meta:
        default_related_name = 'shopping_cart'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'user'),
                name='unique_recipe_user_shopping_cart'
            ),
        )
