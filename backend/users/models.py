from django.contrib.auth.models import AbstractUser
from django.db import models

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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('email',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'
