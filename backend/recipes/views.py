from django.db.models import Exists, OuterRef
# from django.http.response import HttpResponse
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientNameFilter, RecipeFilter
from .models import Favorites, Follow, Ingredient, Purchase, Recipe, Tag, User
from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import (FollowerRecipeSerializer, FollowerSerializer,
                          IngredientSerializer, RecipeSerializer,
                          TagSerializer, UserSerializer)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = [IsOwnerOrAdminOrReadOnly]
    serializer_class = UserSerializer

    @action(detail=True, permission_classes=[IsAuthenticated])
    def subscribe(self, request, user_id):
        user = request.user
        author = get_object_or_404(User, id=user_id)

        if (Follow.objects.filter(user=user, author=author)
                .exists() or user == author):
            return Response({
                'errors': ('Вы уже подписаны на этого пользователя '
                           'или подписываетесь на самого себя')
            }, status=status.HTTP_400_BAD_REQUEST)

        subscribe = Follow.objects.create(user=user, author=author)
        subscribe.save()
        serializer = FollowerSerializer(
            subscribe, context={'request': request}
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, user_id):
        user = request.user
        author = get_object_or_404(User, id=user_id)
        subscribe = Follow.objects.filter(
            user=user, author=author
        )
        if subscribe.exists():
            subscribe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({
            'errors': 'Вы уже отписались'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = Follow.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowerSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientsViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    permission_classes = (AllowAny,)
    filterset_class = IngredientNameFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsOwnerOrAdminOrReadOnly)
    pagination_class = PageNumberPagination
    filter_class = RecipeFilter

    def get_permissions(self):
        if self.action == 'create':
            return IsAuthenticated(),
        if self.action in ['destroy', 'update', 'partial_update']:
            return IsOwnerOrAdminOrReadOnly(),
        return AllowAny(),

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def get_queryset(self):
        user = self.request.user

        if user.is_anonymous:
            return Recipe.objects.all()

        queryset = Recipe.objects.annotate(
            is_favorited=Exists(Favorites.objects.filter(
                user=user, recipe_id=OuterRef('pk')
            )),
            is_in_shopping_cart=Exists(Purchase.objects.filter(
                user=user, recipe_id=OuterRef('pk')
            ))
        )

        if self.request.GET.get('is_favorited'):
            return queryset.filter(is_favorited=True)
        elif self.request.GET.get('is_in_shopping_cart'):
            return queryset.filter(is_in_shopping_cart=True)

        return queryset

    def add_obj(self, model, user, recipe):
        if model.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                'Рецепт уже добавлен в список',
                status=status.HTTP_400_BAD_REQUEST
            )

        obj = model.objects.create(
            user=user, recipe=recipe
        )
        obj.save()
        serializer = FollowerRecipeSerializer(recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_obj(self, model, user, recipe):
        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            'Рецепт уже удален', status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user

        return self.add_obj(Favorites, user, recipe)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        user = request.user
        recipe = self.get_object()

        return self.delete_obj(Favorites, user, recipe)

    @action(detail=True, permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()

        return self.add_obj(Purchase, user, recipe)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = self.get_object()

        return self.delete_obj(Purchase, user, recipe)
