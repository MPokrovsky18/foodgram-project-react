from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from users.constants import MAX_CHARFIELD_LENGTH, MAX_EMAIL_LENGTH


class FoodgramUser(AbstractUser):
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
    subscriber = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    subscribtion = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('subscriber', 'subscribtion'),
                name='unique_subscriber_subscribtion'
            ),
            models.CheckConstraint(
                name='preventing_self_subscription',
                check=~models.Q(subscriber=models.F('subscribtion')),
            )
        )
