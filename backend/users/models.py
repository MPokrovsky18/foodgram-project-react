from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from users.constants import MAX_CHARFIELD_LENGTH, MAX_EMAIL_LENGTH


class FoodgramUser(AbstractUser):
    """Custom user model."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')

    email = models.EmailField(
        'Почта', max_length=MAX_EMAIL_LENGTH, unique=True
    )
    username = models.CharField(
        'Юзернейм',
        max_length=MAX_CHARFIELD_LENGTH,
        validators=(UnicodeUsernameValidator(),),
        unique=True
    )
    first_name = models.CharField('Имя', max_length=MAX_CHARFIELD_LENGTH)
    last_name = models.CharField('Фамилия', max_length=MAX_CHARFIELD_LENGTH)

    class Meta:
        ordering = ('email',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.get_full_name()


class Subscriptions(models.Model):
    """Model to represent user subscriptions."""

    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Автор рецепта'
    )
    subscriber = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Подписчик'
    )

    class Meta:
        ordering = ('author',)
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('subscriber', 'author'),
                name='unique_subscriber_author'
            ),
            models.CheckConstraint(
                name='preventing_self_subscription',
                check=~models.Q(subscriber=models.F('author')),
            )
        )

    def __str__(self):
        return f'{self.subscriber.username} > {self.author.username}'
