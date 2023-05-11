import base64
from django.core.files.base import ContentFile
from django.db.models import F
from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Recipe, Tag, Ingredient, IngredientPortion
from users.models import User, Subscription


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.follows.filter(author=obj).exists()


class Base64ImageField(serializers.ImageField):
    """Custom serializer field for recipe image."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


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

    def get_recipes_count(self, user):
        return user.recipes.count()


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


class ReadIngredientPortionSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientPortion


class ReadRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = ReadIngredientPortionSerializer(many=True, source='portions')
    # ingredients = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()
    
    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favourite', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')
        model = Recipe

    # def get_ingredients(self, recipe):
    #     ingredients = recipe.ingredients.values('id', 'name', 'measurement_unit', amount=F('portions__amount'))
    #     return ingredients

    def get_is_favourite(self, recipe):
        return False

    def get_is_in_shopping_cart(self, recipe):
        return False


class WriteIngredientPortionSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        fields = ('id', 'amount')
        model = IngredientPortion


class WriteRecipeSerializer(serializers.ModelSerializer):
    ingredients = WriteIngredientPortionSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, allow_null=False)
    image = Base64ImageField(required=True)

    class Meta:
        fields = ('ingredients', 'tags', 'image', 'name', 'text', 'cooking_time')
        model = Recipe

    def add_ingredients_and_tags(self, ingredients, tags, recipe):
        recipe.tags.set(tags)
        IngredientPortion.objects.bulk_create(
            [IngredientPortion(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            ) for ingredient in ingredients]
        )
        return recipe

    @atomic
    def create(self, validated_data):
        print(validated_data)
        user = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=user, **validated_data)
        self.add_ingredients_and_tags(ingredients, tags, recipe)
        return recipe

    def to_representation(self, instance):
        context = {'request': self.context['request']}
        return ReadRecipeSerializer(instance, context=context).data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient
