from django_filters import rest_framework as filters
from recipes.models import Recipe


class RecipesFilter(filters.FilterSet):
    """Custom filter for Recipe viewset."""
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        print('is_favorited')
        if value and self.request.user:
            queryset = queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user:
            queryset = queryset.filter(carts__user=self.request.user)
        return queryset

    

