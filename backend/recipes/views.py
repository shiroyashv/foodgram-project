from django.http.response import HttpResponse
from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import RecipeFilter, IngredientNameFilter
from .models import (CustomUser, Favorites, Follow, Ingredient,
                     IngredientInRecipe, Purchase, Recipe, Tag)
from .permissions import IsOwnerOrAdminOrReadOnly
from .serializers import (CreateRecipeSerializer, FollowerRecipeSerializer,
                          FollowerSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrAdminOrReadOnly)
    pagination_class = PageNumberPagination
    filter_class = RecipeFilter

    def get_permissions(self):
        if self.action == 'create':
            return IsAuthenticated(),
        if self.action in ['destroy', 'update', 'partial_update']:
            return IsOwnerOrAdminOrReadOnly(),
        return AllowAny(),

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeSerializer
        return CreateRecipeSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)


class FavoritesViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        recipe_id = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if Favorites.objects.filter(user=user, recipe=recipe).exists():
            return Response('Рецепт уже в избранном.',
                            status=status.HTTP_400_BAD_REQUEST)

        Favorites.objects.create(user=user, recipe=recipe)
        serializer = FollowerRecipeSerializer(recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        recipe_id = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        favorite = get_object_or_404(Favorites, user=user, recipe=recipe)

        if not favorite:
            return Response(
                'Рецепта нет в избранном.',
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response('Рецепт удалён из избранного.',
                        status=status.HTTP_204_NO_CONTENT)


class FollowViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        user = self.request.user
        subscription = CustomUser.objects.filter(following__user=user)

        page = self.paginate_queryset(subscription)
        if page is not None:
            serializer = FollowerSerializer(page, many=True,
                                            context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = FollowerSerializer(subscription, many=True,
                                        context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        user_id = self.kwargs.get('id')
        if user.id == user_id:
            return Response('Нельзя подписаться на самого себя.',
                            status=status.HTTP_400_BAD_REQUEST)

        user_follow = get_object_or_404(CustomUser, pk=user_id)

        if Follow.objects.filter(user=user, author=user_follow).exists():
            return Response('Вы уже подписаны на этого пользователя.',
                            status=status.HTTP_400_BAD_REQUEST)

        Follow.objects.create(user=user, author=user_follow)
        serializer = FollowerSerializer(user_follow,
                                        context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        print('_WTF')
        user = self.request.user
        user_id = self.kwargs.get('id')
        user_follow = get_object_or_404(CustomUser, pk=user_id)

        subscription = get_object_or_404(Follow, user=user,
                                         author=user_follow)

        if not subscription:
            return Response(
                'Вы не подписаны на этого пользователя.',
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response('Подписка отменена.',
                        status=status.HTTP_204_NO_CONTENT)


class IngredientsViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    permission_classes = (AllowAny,)
    filterset_class = IngredientNameFilter


class PurchaseViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        user = self.request.user
        purchase_queryset = user.purchase_list.all()
        purchase_list = {}
        for purchase in purchase_queryset:
            ingredients = IngredientInRecipe.objects.filter(
                recipe=purchase.recipe
            ).prefetch_related('ingredient')

            for ingredient in ingredients:
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                amount = ingredient.amount
                if ingredient.ingredient.name in purchase_list:
                    purchase_list[name]['measurement_unit'] += measurement_unit
                    purchase_list[name]['amount'] += amount
                else:
                    purchase_list[name] = {
                        'measurement_unit': measurement_unit,
                        'amount': amount
                    }
        result_purchase_list = []
        for ingredient, unit in purchase_list.items():
            result_purchase_list.append(
                f"{ingredient} ({unit['measurement_unit']}) — {unit['amount']}"
                + "\n"
            )

        filename = "Purchase_list.txt"
        response = HttpResponse(result_purchase_list,
                                content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format(filename)
        )
        return response

    def get(self, request, *args, **kwargs):
        user = self.request.user
        recipe_id = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if Purchase.objects.filter(user=user, recipe=recipe).exists():
            return Response('Рецепт уже в списке покупок',
                            status=status.HTTP_400_BAD_REQUEST)

        Purchase.objects.create(user=user, recipe=recipe)
        serializer = FollowerRecipeSerializer(recipe)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        recipe_id = self.kwargs.get('id')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        purchase = get_object_or_404(Purchase, user=user, recipe=recipe)

        if not purchase:
            return Response(
                'Рецепта нет в списке покупок.',
                status=status.HTTP_400_BAD_REQUEST
            )
        purchase.delete()
        return Response('Рецепт удалён из списка покупок.',
                        status=status.HTTP_204_NO_CONTENT)
