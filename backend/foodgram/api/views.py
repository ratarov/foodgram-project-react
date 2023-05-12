from django.core.exceptions import ObjectDoesNotExist
from django.db.models.expressions import Case, When
from django.db.models import BooleanField
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import TagSerializer, UserSerializer, IngredientSerializer, SubscriptionSerializer, ReadRecipeSerializer, WriteRecipeSerializer, ShortRecipeSerializer
from api.pagination import PageLimitPagination
# from api.validators import validate_favorite
from recipes.models import Recipe, Tag, Ingredient, Favorite, Cart
from users.models import User, Subscription


class UserViewSet(DjoserUserViewSet):
    """Viewset for users/ endpoints."""
    pagination_class = PageLimitPagination
    queryset = User.objects.all()

    # def get_queryset(self):
    #     user_subs = self.request.user.follows.values_list(
    #         'author', flat=True
    #     ) if self.request.user.is_authenticated else []
    #     return User.objects.annotate(is_subscribed=Case(
    #         When(id__in=user_subs, then=True),
    #         default=False,
    #         output_field=BooleanField()
    #     )).prefetch_related('follows')

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

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated,])
    def subscribe(self, request, id):
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
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ReadRecipeSerializer
        return WriteRecipeSerializer

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated,])
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        relation_exists = user.favorites.filter(recipe=recipe).exists()
        if not relation_exists and request.method == 'POST':
            Favorite.objects.create(user=user, recipe=recipe)
            return Response(ShortRecipeSerializer(recipe).data,
                            status=status.HTTP_201_CREATED)

        elif relation_exists and request.method == 'DELETE':
            favorite_recipe = user.favorites.get(recipe=recipe)
            favorite_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
                data={'detail': 'Ошибка запроса'},
                status=status.HTTP_400_BAD_REQUEST
            )
