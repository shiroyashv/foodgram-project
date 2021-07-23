from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import (CustomUser, Favorites, Follow, Ingredient,
                     IngredientInRecipe, Recipe, Tag)
from .permissions import IsOwnerOrAdmin
from .serializers import (IngredientSerializer, TagSerializer, RecipeSerializer, CreateRecipeSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return IsAuthenticated(),
        if self.action in ['destroy', 'update', 'partial_update']:
            return IsOwnerOrAdmin(),
        return AllowAny(),

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer
        return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context
