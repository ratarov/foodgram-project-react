from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Slug',
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.slug


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=255
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='media/%Y-%m-%d',
    )
    text = models.TextField(
        verbose_name='Текстовое описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientPortion',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(Tag)
    cooking_time = models.SmallIntegerField(
        verbose_name='Время приготовления в минутах',
        validators=[MinValueValidator(1, message='Мин.время - 1 минута')],
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        return self.name


class IngredientPortion(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    amount = models.SmallIntegerField(
        verbose_name='Количество',
        validators=[MinValueValidator(1, message='Мин.кол-во - 1')],
    )

    class Meta:
        verbose_name = 'Порция ингредиента'
        verbose_name_plural = 'Порции ингредиентов'
        default_related_name = 'portions'

    def __str__(self):
        return f'{self.ingredient} in {self.recipe}'
