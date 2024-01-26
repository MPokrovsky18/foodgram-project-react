from django.conf import settings
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models

MAX_CHARFIELD_LENGTH = 200
MAX_COLOR_CHARFIELD_LENGTH = 7
MAX_SLUGFIELD_LENGTH = 200
MIN_VALUE = 1

User = settings.AUTH_USER_MODEL


class Tag(models.Model):
    """
    Model representing a tag for recipes.

    Attributes:
        - name: The name of the tag.
        - color: The color code associated with the tag.
        - slug: The unique slug for the tag.
    """

    name = models.CharField(
        'Название', unique=True, max_length=MAX_CHARFIELD_LENGTH
    )
    color = models.CharField(
        'Цвет', unique=True,
        max_length=MAX_COLOR_CHARFIELD_LENGTH,
        validators=(
            RegexValidator(
                regex='^#[0-9a-fA-F]{6}$', message='Неправильный формат HEX.'
            ),
        )
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
    """
    Model representing an ingredient.

    Attributes:
        - name: The name of the ingredient.
        - measurement_unit: The measurement unit for the ingredient.
        - is_archived: Flag indicating whether the ingredient is archived.

    Methods:
        - to_archive:
            Archive the ingredient and creating an ArchivedIngredient.
        - hard_delete: Perform a hard delete of the ingredient.
        - delete: Soft delete the ingredient,
            archiving it if associated with any Recipe instances.
    """

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
        """Archive the ingredient and creating an ArchivedIngredient."""
        self.is_archived = True
        self.save()
        ArchivedIngredient.objects.create(
            ingredient=self
        )

    def hard_delete(self, *args, **kwargs):
        """Perform a hard delete of the ingredient."""
        super().delete(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Soft delete the ingredient.

        Archiving it if associated with any Recipe instances.
        """
        if IngredientInRecipe.objects.filter(ingredient=self).exists():
            self.to_archive()
        else:
            self.hard_delete(*args, **kwargs)


class ArchivedIngredient(models.Model):
    """
    Model representing an archived ingredient.

    Attributes:
        - ingredient: The original ingredient.
        - archived_at: The timestamp when the ingredient was archived.

    Methods:
        - unarchive:
            Unarchive the ingredient and deleting the ArchivedIngredient.
        - delete: Perform a hard delete of the archived ingredient.
    """

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
        """Unarchive the ingredient and deleting the ArchivedIngredient."""
        self.ingredient.is_archived = False
        self.ingredient.save()
        self.delete()

    def delete(self, *args, **kwargs):
        """Perform a hard delete of the archived ingredient."""
        if self.ingredient.is_archived:
            self.ingredient.hard_delete()

        super().delete(*args, **kwargs)


class Recipe(models.Model):
    """
    Model representing a recipe.

    Attributes:
        - name: The name of the recipe.
        - image: The image associated with the recipe.
        - text: The description of the recipe.
        - coocking_time: The time required to cook the recipe.
        - pub_date: The timestamp when the recipe was published.
        - author: The user who authored the recipe.
        - ingredients: Ingredients used in the recipe.
        - tags: Tags associated with the recipe.

    Methods:
        - is_favorited_by_user(user):
            Check if the given recipe is a favorited of the current user.
        - is_added_to_shopping_list_by_user(user):
            Check if the given recipe has been added
            to the shopping list of the current user.
    """

    name = models.CharField('Название', max_length=MAX_CHARFIELD_LENGTH)
    image = models.ImageField('Изображение', blank=True, null=True)
    text = models.TextField('Описание')
    cooking_time = models.IntegerField('Время приготовления')
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
        through='IngredientInRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagInRecipe',
        related_name='recipes',
        verbose_name='Теги'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name

    def is_favorited_by_user(self, user):
        """Check if the given recipe is a favorited of the current user."""
        return self.favorited_by.filter(id=user.id).exists()

    def is_added_to_shopping_list_by_user(self, user):
        """
        Check if the given recipe has been added
        to the shopping list of the current user.
        """
        return self.added_to_shopping_list_by.filter(id=user.id).exists()


class IngredientInRecipe(models.Model):
    """
    Model representing the relationship between a recipe and its ingredients.

    Attributes:
        - recipe: The recipe associated with the entry.
        - ingredient: The ingredient associated with the entry.
        - quantity: The quantity of the ingredient used in the recipe.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        'Количество',
        default=MIN_VALUE,
        validators=(
            MinValueValidator(
                MIN_VALUE,
                message=('Количество ингредиента '
                         'не может быть меньше {MIN_VALUE}.')
            ),
        )
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_recipe_ingredient'
            )
        ]
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'


class TagInRecipe(models.Model):
    """
    Model representing the relationship between a recipe and its tegs.

    Attributes:
        - recipe: The recipe associated with the entry.
        - tag: The tag associated with the entry.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'tag'),
                name='unique_recipe_tag'
            )
        ]
        verbose_name = 'тег рецепта'
        verbose_name_plural = 'Теги рецепта'
