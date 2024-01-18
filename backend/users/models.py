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
        blank=True,
        null=True,
        verbose_name='Избранные рецепты'
    )
    shopping_list = models.ManyToManyField(
        Recipe,
        related_name='added_to_shopping_list_by',
        blank=True,
        null=True,
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
