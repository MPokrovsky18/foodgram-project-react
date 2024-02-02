from api import serializers
from api.decorators import add_remove_action
from api.filters import IngredientFilter, RecipeFilter
from api.ingredient_utls import get_ingredients_amount
from api.permissions import IsAuthorOrReadOnly
from django.http import HttpResponse
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import Ingredient, Recipe, Tag
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet


class TagReadOnlyViewSet(ReadOnlyModelViewSet):
    """ViewSet providing read-only access to Tag objects."""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None


class IngredientReadOnlyViewSet(ReadOnlyModelViewSet):
    """ViewSet providing read-only access to Ingredient objects."""

    serializer_class = serializers.IngredientSerializer
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
    serializer_class = serializers.RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_object(self):
        if (
            self.action in ('favorite', 'shopping_cart')
            and self.request.method == 'POST'
        ):
            return Recipe.objects.filter(
                id=self.kwargs[self.lookup_field]
            ).first()

        return super().get_object()

    def get_serializer_class(self):
        if self.action in ('favorite', 'shopping_cart'):
            return serializers.RecipeMinifiedSerializer

        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in (
            'favorite', 'shopping_cart', 'download_shopping_cart'
        ):
            return (IsAuthenticated(),)

        return super().get_permissions()

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

    @action(detail=False)
    def download_shopping_cart(self, request):
        return HttpResponse(
            render_to_string(
                'api/shopping_cart.txt',
                {
                    'ingredients_amount': get_ingredients_amount(request.user),
                    'username': request.user.username
                }
            ),
            content_type='text/plain'
        )


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
            return serializers.UserWithRecipesSerializer

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
