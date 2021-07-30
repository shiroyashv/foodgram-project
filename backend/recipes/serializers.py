from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.models import CustomUser
from users.serializers import UserSerializer

from .models import (Favorites, Ingredient, IngredientInRecipe, Purchase,
                     Recipe, Tag)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('__all__')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'amount', 'measurement_unit')
        read_only_fields = ('amount',)


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='ingredients_amount', many=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'text', 'image',
                  'ingredients', 'tags', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')

        def get_is_favorited(self, obj):
            recipe = get_object_or_404(Recipe, id=obj.id)
            user = self.context['request'].user
            if user.is_anonymous:
                return False
            return Favorites.objects.filter(recipe=recipe, user=user).exists()

        def get_is_in_shopping_cart(self, obj):
            recipe = get_object_or_404(Recipe, id=obj.id)
            user = self.context['request'].user
            if user.is_anonymous:
                return False
            return Purchase.objects.filter(recipe=recipe, user=user).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    author = UserSerializer(read_only=True)
    ingredients = AddIngredientToRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        ingredients_set = set()
        for ingredient in ingredients_data:
            if ingredient['amount'] < 0:
                raise serializers.ValidationError(
                    'Количество должно быть >= 0')
            if ingredient['id'] in ingredients_set:
                raise serializers.ValidationError(
                    'Ингредиент в рецепте не должен повторяться.')
            ingredients_set.add(ingredient['id'])
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients_data:
            amount = ingredient['amount']
            id = ingredient['id']
            IngredientInRecipe.objects.create(
                ingredient=get_object_or_404(Ingredient, id=id),
                recipe=recipe, amount=amount
            )
        for tag in tags_data:
            recipe.tags.add(tag)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        ingredients_set = set()
        for ingredient in ingredients_data:
            if ingredient['amount'] < 0:
                raise serializers.ValidationError(
                    'Количество должно быть >= 0')
            if ingredient['id'] in ingredients_set:
                raise serializers.ValidationError(
                    'Ингредиент в рецепте не должен повторяться.')
            ingredients_set.add(ingredient['id'])
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        for ingredient in ingredients_data:
            amount = ingredient['amount']
            id = ingredient['id']
            IngredientInRecipe.objects.create(
                ingredient=get_object_or_404(Ingredient, id=id),
                recipe=instance, amount=amount
            )
        for tag in tags_data:
            instance.tags.add(tag)
        instance.save()
        return instance

    def to_representation(self, instance):
        data = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data
        return data


class FollowerRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowerSerializer(UserSerializer):
    recipes = FollowerRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, user):
        return user.recipes.count()
