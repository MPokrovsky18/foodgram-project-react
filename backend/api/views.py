from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from api.decorators import recipe_action
from api.filters import IngredientFilter, RecipeFilter
from api.serializers import (
    IngredientSerializer, RecipeSerializer, TagSerializer,
)
from recipes.models import Ingredient, Recipe, Tag


class TagReadOnlyViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter

    def get_queryset(self):
        return Ingredient.objects.filter(is_archived=False)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'])
    @recipe_action
    def favorite(self, user, recipe, remove=False):
        if remove:
            user.remove_from_favorites(recipe)
        else:
            user.add_to_favorites(recipe)

    @action(detail=True, methods=['post', 'delete'])
    @recipe_action
    def shopping_cart(self, user, recipe, remove=False):
        if remove:
            user.remove_from_shopping_list(recipe)
        else:
            user.add_to_shopping_list(recipe)
