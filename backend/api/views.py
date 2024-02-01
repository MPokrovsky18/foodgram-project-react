from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.decorators import add_remove_action
from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    IngredientSerializer, RecipeSerializer, RecipeMinifiedSerializer,
    TagSerializer, UserWithRecipesSerializer
)
from recipes.models import Ingredient, Recipe, Tag


class TagReadOnlyViewSet(ReadOnlyModelViewSet):
    """ViewSet providing read-only access to Tag objects."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientReadOnlyViewSet(ReadOnlyModelViewSet):
    """ViewSet providing read-only access to Ingredient objects."""

    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter

    def get_queryset(self):
        """Retrieve the queryset of non-archived ingredients."""
        return Ingredient.objects.filter(is_archived=False)


class RecipeViewSet(ModelViewSet):
    """
    ViewSet providing CRUD operations for Recipe objects.

    Additing actions for favoriting and adding/removing from the shopping cart.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
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
        """Action to favorite or unfavorite a recipe for the current user."""
        if remove:
            user.remove_from_favorites(recipe)
        else:
            user.add_to_favorites(recipe)

    @add_remove_action
    def shopping_cart(self, user, recipe, remove=False):
        """Action to add or remove a recipe from the shopping cart."""
        if remove:
            user.remove_from_shopping_list(recipe)
        else:
            user.add_to_shopping_list(recipe)


class FoodgramUserViewSet(UserViewSet):
    """
    Custom UserViewSet.

    Add actions for retrieving user subscriptions,
    subscribing and unsubscribing.
    """

    def get_permissions(self):
        if self.action in ('me', 'subscriptions', 'subscribe'):
            return (IsAuthenticated(),)

        return super().get_permissions()

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
        """Action to retrieve the list of user subscriptions."""
        return super().list(request)

    @add_remove_action
    def subscribe(self, current_user, user, remove=False):
        """Action to subscribe or unsubscribe the current user."""
        if remove:
            current_user.unsubscribe(user)
        else:
            current_user.subscribe(user)
