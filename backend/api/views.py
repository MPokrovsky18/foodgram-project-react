from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from api.decorators import add_remove_action
from api.filters import IngredientFilter, RecipeFilter
from api.serializers import (
    IngredientSerializer, RecipeSerializer, RecipeMinifiedSerializer,
    TagSerializer, UserWithRecipesSerializer
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

    def get_serializer_class(self):
        if self.action in ('favorite', 'shopping_cart'):
            return RecipeMinifiedSerializer

        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @add_remove_action
    def favorite(self, user, recipe, remove=False):
        if remove:
            user.remove_from_favorites(recipe)
        else:
            user.add_to_favorites(recipe)

    @add_remove_action
    def shopping_cart(self, user, recipe, remove=False):
        if remove:
            user.remove_from_shopping_list(recipe)
        else:
            user.add_to_shopping_list(recipe)


class FoodgramUserViewSet(UserViewSet):
    def get_serializer_class(self):
        if self.action in ('subscriptions', 'subscribe'):
            return UserWithRecipesSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        if self.action == 'subscriptions':
            return self.request.user.subscriptions.all()

        return super().get_queryset()

    @action(detail=False)
    def subscriptions(self, request):
        return super().list(request)

    @add_remove_action
    def subscribe(self, current_user, user, remove=False):
        if remove:
            current_user.unsubscribe(user)
        else:
            current_user.subscribe(user)
