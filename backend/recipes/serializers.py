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
    class Meta:
        model = IngredientInRecipe
        fields = '__all__'


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

        def get_ingredients(self, obj):
            ingredients = IngredientInRecipe.objects.filter(recipe=obj)
            return IngredientInRecipeSerializer(ingredients, many=True).data

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
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        author = self.context.get('request').user
        recipe = Recipe(author=author, **validated_data)

        recipe_ingredient_list = []
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            if amount < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0.'
                )

            ingredient_instance = get_object_or_404(Ingredient,
                                                    id=ingredient.get('id'))
            recipe_ingredient_list.append(IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient_instance,
                amount=amount
            ))

        recipe.save()
        recipe.tags.set(tags)
        IngredientInRecipe.objects.bulk_create(recipe_ingredient_list)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe_ingredient_list = []
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            if amount < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0.'
                )
            ingredient_instance = get_object_or_404(
                Ingredient, id=ingredient.get('id')
            )
            recipe_ingredient_list.append(IngredientInRecipe(
                recipe=instance,
                ingredient=ingredient_instance,
                amount=amount
            ))

        IngredientInRecipe.objects.filter(recipe=instance).delete()
        instance.name = validated_data.get('name')
        instance.image = validated_data.get('image')
        instance.text = validated_data.get('text')
        instance.cooking_time = validated_data.get('cooking_time')
        instance.save()
        instance.tags.set(tags)
        IngredientInRecipe.objects.bulk_create(recipe_ingredient_list)

        return instance


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
