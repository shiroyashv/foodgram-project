import django_filters as filters

from .models import Ingredient, Recipe


class IngredientNameFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', method='name_starts_with')

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')

    def name_starts_with(self, queryset, slug, name):
        return queryset.filter(name__startswith=name)


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )
    is_favorited = filters.BooleanFilter()
    is_in_shopping_cart = filters.BooleanFilter()

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_favorite(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(favorite_recipe__user=user)
        return Recipe.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(customers__user=user)
        return Recipe.objects.all()
