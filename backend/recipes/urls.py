from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (FavoritesViewSet, FollowViewSet, IngredientsViewSet,
                    PurchaseViewSet, RecipeViewSet, TagViewSet)

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')

urlpatterns = [
    path('recipes/download_shopping_cart/',
         PurchaseViewSet.as_view({'get': 'list'})),
    path('recipes/<int:id>/shopping_cart/',
         PurchaseViewSet.as_view({'get': 'get', 'delete': 'delete'})),
    path('recipes/<int:id>/favorite/',
         FavoritesViewSet.as_view({'get': 'get', 'delete': 'delete'})),
    path('users/subscriptions/',
         FollowViewSet.as_view({'get': 'list'})),
    path('users/<int:id>/subscribe/',
         FollowViewSet.as_view({'get': 'get', 'delete': 'delete'})),
]

urlpatterns += router.urls
