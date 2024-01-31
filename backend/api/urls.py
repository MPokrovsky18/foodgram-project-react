from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    IngredientReadOnlyViewSet, TagReadOnlyViewSet,
    RecipeViewSet, FoodgramUserViewSet
)


namespace = 'api'

router_v1 = DefaultRouter()
router_v1.register(
    r'tags',
    TagReadOnlyViewSet,
    basename='tags'
)
router_v1.register(
    r'ingredients',
    IngredientReadOnlyViewSet,
    basename='ingredients'
)
router_v1.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)
router_v1.register(
    r'users',
    FoodgramUserViewSet,
    basename='users'
)

urlpatterns_v1 = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns = [
    path('', include(urlpatterns_v1)),
]
