import base64
from django.core.files.base import ContentFile
from django.db.transaction import atomic
from rest_framework import serializers

from recipes.models import Recipe, Tag, Ingredient, IngredientPortion
from users.models import User


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient viewset."""
    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Additional serializer for Recipes with short list of fields.
    Used for Subscriptions, Favorite Recipes and Shopping Cart.
    """
    class Meta:
        fields = ('id', 'name', 'image', 'cooking_time')
        model = Recipe


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag viewset."""
    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class Base64ImageField(serializers.ImageField):
    """Custom serializer field for recipe image."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User viewset."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.follows.filter(author=obj).exists()


class SubscriptionSerializer(UserSerializer):
    """Serializer for User's Subscriptions. Based on User serializer."""
    recipes = ShortRecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_fields = (
            'email', 'id', 'username', 'last_name', 'first_name', 'read_only')

    def get_recipes_count(self, user):
        return user.recipes.count()

    def validate(self, attrs):
        user = self.context['request'].user
        author = self.context['author']
        if user == author:
            raise serializers.ValidationError('Нельзя подписаться на себя.')
        return attrs


class ReadIngredientPortionSerializer(serializers.ModelSerializer):
    """IngredientPortion nested field for Recipe requests with safe methods."""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientPortion


class ReadRecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe requests with safe methods."""
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = ReadIngredientPortionSerializer(many=True, source='portions')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')
        model = Recipe

    def get_is_favorited(self, recipe):
        user = self.context['request'].user
        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context['request'].user
        return user.carts.filter(recipe=recipe).exists()


class WriteIngredientPortionSerializer(serializers.ModelSerializer):
    """IngredientPortion nested field for Recipe requests w/ unsafe methods."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        fields = ('id', 'amount')
        model = IngredientPortion


class WriteRecipeSerializer(serializers.ModelSerializer):
    """Serializer for Recipe requests with unsafe methods."""
    ingredients = WriteIngredientPortionSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    image = Base64ImageField(required=True)

    class Meta:
        fields = ('ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')
        model = Recipe

    def validate(self, attrs):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        if not tags or not ingredients:
            raise serializers.ValidationError(
                'Теги и ингредиенты - обязательные реквизиты рецепта.')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Теги не должны повторяться.')
        return attrs

    def _add_ingredients_and_tags(self, ingredients, tags, recipe):
        recipe.tags.set(tags)
        IngredientPortion.objects.bulk_create([IngredientPortion(
            recipe=recipe,
            ingredient=ingredient['id'],
            amount=ingredient['amount'],
        ) for ingredient in ingredients])
        return recipe

    @atomic
    def create(self, validated_data):
        user = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=user, **validated_data)
        self._add_ingredients_and_tags(ingredients, tags, recipe)
        return recipe

    @atomic
    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe.tags.clear()
        recipe.ingredients.clear()
        self._add_ingredients_and_tags(ingredients, tags, recipe)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        context = {'request': self.context['request']}
        return ReadRecipeSerializer(instance, context=context).data
