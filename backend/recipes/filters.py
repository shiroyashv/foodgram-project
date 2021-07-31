import django_filters as filters

from .models import Ingredient, Recipe, User


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
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author']
