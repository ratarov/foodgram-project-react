from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipesFilter
from api.pagination import PageLimitPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (IngredientSerializer, ReadRecipeSerializer,
                             ShortRecipeSerializer, SubscriptionSerializer,
                             TagSerializer, WriteRecipeSerializer)
from users.models import Subscription, User


class UserViewSet(DjoserUserViewSet):
    """
    Viewset for users/ endpoints, based on Djoser viewset template.
    Options: registration, user profile, current user (/me), change password,
    + subscriptions for other users: add/del/list actions.
    """
    pagination_class = PageLimitPagination
    queryset = User.objects.all()

    @action(methods=['GET'], detail=False, url_path='subscriptions')
    def user_subscriptions(self, request):
        qs = self.queryset.filter(followers__follower=request.user)
        paginated_qs = self.paginate_queryset(qs)
        serializer = SubscriptionSerializer(
            paginated_qs,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=[IsAuthenticated,],
            url_path='subscribe')
    def add_del_subscription(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscribed = user.follows.filter(author=author).exists()
        if not subscribed and request.method == 'POST':
            serializer = SubscriptionSerializer(
                author,
                data={},
                context={'request': request, 'author': author}
            )
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(follower=user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        elif subscribed and request.method == 'DELETE':
            subscription = user.follows.get(author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(data={'detail': 'Ошибка запроса'},
                        status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for tags/ endpoints: list/retrieve actions.
    Read-only, all changes via admin-panel only.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Viewset for ingredients/ endpoints: list/retrieve actions.
    Read-only, all changes via admin-panel only.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientSearchFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Viewset for recipes/ endpoints: standard CRUD actions,
                                    changes are only for author of object
    + favorites recipes: add/del actions,
    + recipes for shopping: add/del actions, download file with list
                            of unique ingredients.
    """
    queryset = (Recipe.objects.all().
                select_related('author').
                prefetch_related('tags', 'portions', 'portions__ingredient'))
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    def _add_or_del_relation(self, model, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        rel_exists = model.objects.filter(user=user, recipe=recipe).exists()

        if not rel_exists and request.method == 'POST':
            model.objects.create(user=user, recipe=recipe)
            return Response(ShortRecipeSerializer(recipe).data,
                            status=status.HTTP_201_CREATED)

        elif rel_exists and request.method == 'DELETE':
            relation = model.objects.get(user=user, recipe=recipe)
            relation.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(data={'detail': 'Неверный запрос'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=[IsAuthenticated],
            url_path='favorite')
    def add_del_favorite_recipe(self, request, pk):
        return self._add_or_del_relation(Favorite, request, pk)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=[IsAuthenticated],
            url_path='shopping_cart')
    def add_del_recipe_in_shopping_cart(self, request, pk):
        return self._add_or_del_relation(Cart, request, pk)

    @action(methods=['GET'],
            detail=False,
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        shopping_list = request.user.get_shopping_list()
        response = HttpResponse(shopping_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = ('attachment; filename='
                                           f'{settings.SHOP_LIST_FILE}')
        return response
