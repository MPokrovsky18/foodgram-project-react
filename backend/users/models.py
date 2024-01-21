from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models

from recipes.models import Recipe

MAX_CHARFIELD_LENGTH = 150
MAX_EMAIL_LENGTH = 254


class FoodgramUser(AbstractUser):
    email = models.EmailField(
        'Почта', max_length=MAX_EMAIL_LENGTH, unique=True
    )
    username = models.CharField(
        'Имя пользователя', max_length=MAX_CHARFIELD_LENGTH, unique=True
    )
    first_name = models.CharField('Имя', max_length=MAX_CHARFIELD_LENGTH)
    last_name = models.CharField('Фамилия', max_length=MAX_CHARFIELD_LENGTH)
    subscriptions = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='subscribers',
        verbose_name='Подписки'
    )
    favorite_recipes = models.ManyToManyField(
        Recipe,
        related_name='favorited_by',
        verbose_name='Избранные рецепты'
    )
    shopping_list = models.ManyToManyField(
        Recipe,
        related_name='added_to_shopping_list_by',
        verbose_name='Список покупок'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('email',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

    def subscribe(self, user):
        if user == self:
            raise ValidationError('Нельзя подписаться на самого себя!')

        if self.subscriptions.filter(id=user.id).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя!')

        self.subscriptions.add(user)

    def unsubscribe(self, user):
        if not self.subscriptions.filter(id=user.id).exists():
            raise ValidationError(
                'Вы не подписаны на этого пользователя!'
            )

        self.subscriptions.remove(user)

    def add_to_favorites(self, recipe):
        if self.favorite_recipes.filter(id=recipe.id).exists():
            raise ValidationError(
                'Вы уже добавили этот рецепт в Избранное!'
            )

        self.favorite_recipes.add(recipe)

    def remove_from_favorites(self, recipe):
        if not self.favorite_recipes.filter(id=recipe.id).exists():
            raise ValidationError(
                'Вы еще не добавили этот рецепт в Избранное!'
            )

        self.favorite_recipes.remove(recipe)

    def add_to_shopping_list(self, recipe):
        if self.shopping_list.filter(id=recipe.id).exists():
            raise ValidationError(
                'Вы уже добавили этот рецепт в Список покупок!'
            )

        self.shopping_list.add(recipe)

    def remove_from_shopping_list(self, recipe):
        if not self.shopping_list.filter(id=recipe.id).exists():
            raise ValidationError(
                'Вы еще не добавили этот рецепт в Список покупок!'
            )

        self.shopping_list.remove(recipe)
