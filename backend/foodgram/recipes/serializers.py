from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from .models import (Favorites, Follow, Ingredient,
                     IngredientInRecipe, Recipe, Tag)
from users.serializers import UserSerializer


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


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        max_length=None,
        required=True,
        allow_empty_file=False,
        use_url=True,
    )
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

        def get_ingredients(self, obj):
            ingredients = IngredientInRecipe.objects.filter(recipe=obj)
            return IngredientInRecipeSerializer(ingredients, many=True).data

        def get_is_favorited(self, obj):
            request = self.context.get('request')
            user = request.user
            return Favorites.objects.filter(recipe=obj, user=user).exists()


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


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
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(
            author=author, **validated_data)
        recipe.save()
        recipe.tags.set(tags_data)
        for ingredient in ingredients_data:
            ingredient_model = Ingredient.objects.get(id=ingredient['id'])
            amount = ingredient['amount']
            IngredientInRecipe.objects.create(
                ingredient=ingredient_model,
                recipe=recipe,
                amount=amount
            )
        return recipe

    def update(self, instance, validated_data):
        ingredient_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        for new_ingredient in ingredient_data:
            IngredientInRecipe.objects.create(
                ingredient=Ingredient.objects.get(id=new_ingredient['id']),
                recipe=instance,
                amount=new_ingredient['amount']
            )
        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        if validated_data.get('image') is not None:
            instance.image = validated_data.pop('image')
        instance.cooking_time = validated_data.pop('cooking_time')
        instance.save()
        instance.tags.set(tags_data)
        return instance

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data
