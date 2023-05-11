from django.contrib import admin

from recipes.models import Recipe, Ingredient, IngredientPortion, Tag


class IngredientPortionAdmin(admin.TabularInline):
    model = IngredientPortion
    # fields = ('ingredient.name', 'ingredient.measurement_unit')


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
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
    )
    inlines = (IngredientPortionAdmin,)
    search_fields = ('name', 'author', 'tags')
    autocomplete_fields = ['tags']
    list_filter = ('author', 'name')
    empty_value_display = '-пусто-'
