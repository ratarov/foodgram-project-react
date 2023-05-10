from django.contrib import admin

from recipes.models import Recipe, Ingredient, IngredientPortion, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    search_fields = ('name', 'slug')
    list_filter = ('id', 'name', 'color', 'slug')
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class Ingredientdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'