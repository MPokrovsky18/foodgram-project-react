from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from api.serializers import (
    IngredientSerializer, RecipeSerializer, TagSerializer
)
from recipes.models import Ingredient, Recipe, Tag


class IngredientReadOnlyViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer

    def get_queryset(self):
        return Ingredient.objects.filter(is_archived=False)


class TagReadOnlyViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
