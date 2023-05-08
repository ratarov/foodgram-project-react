from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin)

from users.managers import UserManager


validate_username = UnicodeUsernameValidator()


class User(AbstractBaseUser, PermissionsMixin):
    """Customs user model with email for authentication."""
    email = models.EmailField(
        verbose_name='Email', max_length=255, unique=True,
    )
    username = models.CharField(
        verbose_name='Логин', max_length=150, unique=True,
        validators=[validate_username],
    )
    first_name = models.CharField(
        verbose_name='Имя', max_length=255,
    )
    last_name = models.CharField(
        verbose_name='Фамилия', max_length=255,
    )
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
