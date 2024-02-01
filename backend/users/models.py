from django.core.exceptions import ValidationError
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractUser
from django.db import models

from recipes.models import Recipe

MAX_CHARFIELD_LENGTH = 150
MAX_EMAIL_LENGTH = 254


class FoodgramUser(AbstractUser):
    """
    Custom user model for Foodgram application.

    Attributes:
        - email: User's unique email.
        - username: User's unique username.
        - first_name: User's first name.
        - last_name: User's last name.
        - subscriptions: Users the current user is subscribed to.
        - favorite_recipes: Recipes marked as favorites by the user.
        - shopping_list: Recipes in the user's shopping list.

    Methods:
        - is_subscriber(user):
            Check if the given user is a subscriber of the current user.
        - subscribe(user): Subscribe the user to another user.
        - unsubscribe(user): Unsubscribe the user from another user.
        - add_to_favorites(recipe): Add a recipe to the user's favorites.
        - remove_from_favorites(recipe): Remove a recipe from favorites.
        - add_to_shopping_list(recipe): Add a recipe to shopping list.
        - remove_from_shopping_list(recipe):
            Remove a recipe from shopping list.
    """

    email = models.EmailField(
        'Почта', max_length=MAX_EMAIL_LENGTH, unique=True
    )
    username = models.CharField(
        'Юзернейм',
        max_length=MAX_CHARFIELD_LENGTH,
        validators=(UnicodeUsernameValidator(),),
        unique=True
    )
    password = models.CharField('Пароль', max_length=MAX_CHARFIELD_LENGTH)
    first_name = models.CharField('Имя', max_length=MAX_CHARFIELD_LENGTH)
    last_name = models.CharField('Фамилия', max_length=MAX_CHARFIELD_LENGTH)
    subscriptions = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='subscribers',
        verbose_name='Подписки'
    )
    favorite_recipes = models.ManyToManyField(
        Recipe,
        blank=True,
        related_name='favorited_by',
        verbose_name='Избранные рецепты'
    )
    shopping_list = models.ManyToManyField(
        Recipe,
        blank=True,
        related_name='added_to_shopping_list_by',
        verbose_name='Список покупок'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        ordering = ('email',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def is_subscriber(self, user):
        """
        Check if the given user is a subscriber of the current user.

        Args:
            user (FoodgramUser): User to check for subscription.

        Returns:
            bool: True if the given user is a subscriber, False otherwise.
        """
        return self.subscribers.filter(id=user.id).exists()

    def subscribe(self, user):
        """
        Subscribe the user to another user.

        Args:
            user (FoodgramUser): User to subscribe to.

        Raises:
            ValidationError:
                If attempting to subscribe to oneself
                or already subscribed to the user.
        """
        if user == self:
            raise ValidationError('Нельзя подписаться на самого себя!')

        if self.subscriptions.filter(id=user.id).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя!')

        self.subscriptions.add(user)

    def unsubscribe(self, user):
        """
        Unsubscribe the user from another user.

        Args:
            user (FoodgramUser): User to unsubscribe from.

        Raises:
            ValidationError: If not already subscribed to the user.
        """
        if not self.subscriptions.filter(id=user.id).exists():
            raise ValidationError(
                'Вы не подписаны на этого пользователя!'
            )

        self.subscriptions.remove(user)

    def add_to_favorites(self, recipe):
        """
        Add a recipe to the user's favorites.

        Args:
            recipe (Recipe): Recipe to add to favorites.

        Raises:
            ValidationError: If the recipe is already in the user's favorites.
        """
        if self.favorite_recipes.filter(id=recipe.id).exists():
            raise ValidationError(
                'Вы уже добавили этот рецепт в Избранное!'
            )

        self.favorite_recipes.add(recipe)

    def remove_from_favorites(self, recipe):
        """
        Remove a recipe from the user's favorites.

        Args:
            recipe (Recipe): Recipe to remove from favorites.

        Raises:
            ValidationError: If the recipe is not in the user's favorites.
        """
        if not self.favorite_recipes.filter(id=recipe.id).exists():
            raise ValidationError(
                'Вы еще не добавили этот рецепт в Избранное!'
            )

        self.favorite_recipes.remove(recipe)

    def add_to_shopping_list(self, recipe):
        """
        Add a recipe to the user's shopping list.

        Args:
            recipe (Recipe): Recipe to add to the shopping list.

        Raises:
            ValidationError: If the recipe is already in the shopping list.
        """
        if self.shopping_list.filter(id=recipe.id).exists():
            raise ValidationError(
                'Вы уже добавили этот рецепт в Список покупок!'
            )

        self.shopping_list.add(recipe)

    def remove_from_shopping_list(self, recipe):
        """
        Remove a recipe from the user's shopping list.

        Args:
            recipe (Recipe): Recipe to remove from the shopping list.

        Raises:
            ValidationError: If the recipe is not in the shopping list.
        """
        if not self.shopping_list.filter(id=recipe.id).exists():
            raise ValidationError(
                'Вы еще не добавили этот рецепт в Список покупок!'
            )

        self.shopping_list.remove(recipe)
