from api import views
from django.urls import include, path
from rest_framework.routers import DefaultRouter

namespace = 'api'

router_v1 = DefaultRouter()
router_v1.register(
    r'tags',
    views.TagReadOnlyViewSet,
    basename='tags'
)
router_v1.register(
    r'ingredients',
    views.IngredientReadOnlyViewSet,
    basename='ingredients'
)
router_v1.register(
    r'recipes',
    views.RecipeViewSet,
    basename='recipes'
)
router_v1.register(
    r'users',
    views.FoodgramUserViewSet,
    basename='users'
)

urlpatterns_v1 = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns = [
    path('', include(urlpatterns_v1)),
]
