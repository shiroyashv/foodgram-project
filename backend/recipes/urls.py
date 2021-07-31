from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientsViewSet, RecipeViewSet,
                    TagViewSet)

app_name = 'recipes'

router = DefaultRouter()

router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls))
]
