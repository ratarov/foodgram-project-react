from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

# from api.views import TagViewSet
from recipes.models import Recipe, Tag, Ingredient
from users.models import User, Subscription


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(read_only=True)

    class Meta:
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed')
        model = User


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class ReadSubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(read_only=True)
    recipes = ShortRecipeSerializer(read_only=True, many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')
        model = User

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class NewSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('follower', 'author')
        model = Subscription
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('follower', 'author'),
                message='Нельзя подписаться на автора более 1 раза.',
            )
        ]

    def validate(self, attrs):
        if self.context['request'].user.id == self.initial_data['author']:
            raise serializers.ValidationError('Нельзя подписаться на себя.')
        return attrs


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


# class WriteRecipeSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = ()
#         model = Recipe


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favourite', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')
        model = Recipe
    

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient