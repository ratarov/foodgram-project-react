from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models.aggregates import Sum
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin)

from users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Customs user model with email for authentication."""
    email = models.EmailField(
        verbose_name='Email', max_length=255, unique=True)
    username = models.CharField(
        verbose_name='Логин', max_length=150, unique=True,
        validators=[UnicodeUsernameValidator])
    first_name = models.CharField(
        verbose_name='Имя', max_length=255)
    last_name = models.CharField(
        verbose_name='Фамилия', max_length=255)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def get_shopping_list(self):
        ingredients = (self.carts.values(
                'recipe__ingredients__name',
                'recipe__ingredients__measurement_unit',
                'recipe__portions__amount',
            ).
            annotate(total=Sum('recipe__portions__amount')).
            order_by('recipe__ingredients__name'))
        shopping_list = [f'Список покупок для {self.first_name} '
                         f'{self.last_name}:']
        for ingredient in ingredients:
            shopping_list.append(
                f"\n - {ingredient['recipe__ingredients__name']} "
                f"({ingredient['recipe__ingredients__measurement_unit']}): "
                f"{ingredient['total']}"
            )
        return shopping_list


class Subscription(models.Model):
    """
    Subscription model allows user to follow another user that
    publishes recipes.
    """
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follows',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['follower', 'author'],
                                    name='Уникальная подписка'),
            models.CheckConstraint(
                check=~models.Q(author=models.F('follower')),
                name='Нельзя подписаться на себя'),
        ]

    def __str__(self):
        return f'{self.follower} follows {self.author}'
