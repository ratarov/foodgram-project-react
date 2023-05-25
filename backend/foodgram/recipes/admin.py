from django.contrib import admin

from recipes.models import (Cart, Favorite, Ingredient, IngredientPortion,
                            Recipe, Tag)


class IngredientPortionAdmin(admin.TabularInline):
    model = IngredientPortion


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
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'added_to_favorites',
    )
    inlines = (IngredientPortionAdmin,)
    search_fields = ('name', 'tags')
    autocomplete_fields = ['tags']
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-пусто-'

    def added_to_favorites(self, obj):
        return obj.favorites.count()

    added_to_favorites.short_description = 'В избранном'


class UserRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
    search_fields = ('user', 'recipe')
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(UserRecipeAdmin):
    pass


@admin.register(Cart)
class CartAdmin(UserRecipeAdmin):
    pass
