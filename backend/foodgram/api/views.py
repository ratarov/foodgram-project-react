from django.core.exceptions import ObjectDoesNotExist
from django.db.models.expressions import Case, When
from django.db.models import BooleanField
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers import TagSerializer, RecipeSerializer, UserSerializer, IngredientSerializer, ReadSubscriptionSerializer, NewSubscriptionSerializer
from api.pagination import PageLimitPagination
from recipes.models import Recipe, Tag, Ingredient
from users.models import User, Subscription


class UserViewSet(DjoserUserViewSet):
    """Viewset for users/ endpoints."""
    pagination_class = PageLimitPagination

    def get_queryset(self):
        user_subs = self.request.user.follows.values_list(
            'author', flat=True
        ) if self.request.user.is_authenticated else []
        return User.objects.annotate(is_subscribed=Case(
            When(id__in=user_subs, then=True),
            default=False,
            output_field=BooleanField()
        )).prefetch_related('follows')

    @action(methods=['GET'], detail=False, url_path='subscriptions')
    def user_subscribtions(self, request):
        qs = self.queryset.filter(followers__follower=request.user)
        paginated_qs = self.paginate_queryset(qs)
        serializer = ReadSubscriptionSerializer(paginated_qs, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[IsAuthenticated,])
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = NewSubscriptionSerializer(
                data={'follower': user.id, 'author': author.id},
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(ReadSubscriptionSerializer(author).data,
                            status=status.HTTP_201_CREATED)
        try:
            sub = user.follows.get(author=author)
        except ObjectDoesNotExist:
            return Response(data={'detail': 'Подписка не найдена'},
                            status=status.HTTP_400_BAD_REQUEST)
        sub.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
