from django.db.models import Exists, F, Sum, Value, IntegerField, OuterRef
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api import serializers
from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from recipes.models import (
    Ingredient, IngredientInRecipe, Recipe, Tag, Favourites, ShoppingCart
)
from users.models import Subscriptions


class TagReadOnlyViewSet(ReadOnlyModelViewSet):
    """ViewSet providing read-only access to Tag objects."""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None


class IngredientReadOnlyViewSet(ReadOnlyModelViewSet):
    """ViewSet providing read-only access to Ingredient objects."""

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet):
    """
    ViewSet providing CRUD operations for Recipe objects.

    Additing actions for favoriting and adding/removing from the shopping cart.
    """

    queryset = Recipe.objects.all(
    ).select_related('author').prefetch_related(
        'tags', 'ingredients'
    )
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return super().get_queryset().annotate(
                is_favorited=Exists(
                    Favourites.objects.filter(
                        recipe=OuterRef('pk'),
                        user=self.request.user)
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        recipe=OuterRef('pk'),
                        user=self.request.user)
                )
            )

        return super().get_queryset()

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return serializers.RecipeGetSerializer

        return serializers.RecipePostSerializer

    def get_permissions(self):
        if self.action in (
            'favorite', 'shopping_cart', 'download_shopping_cart'
        ):
            return (IsAuthenticated(),)

        return super().get_permissions()

    @staticmethod
    def write_recipe_to(request, serializer_class, pk):
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        serializer = serializer_class(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @staticmethod
    def delete_recipe_from(request, source_model, pk):
        delete_recipe = get_object_or_404(
            source_model, recipe=pk, user=request.user.id
        )
        delete_recipe.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True, methods=('post',))
    def favorite(self, request, pk):
        return self.write_recipe_to(
            request, serializers.FavoriteSerializer, pk
        )

    @action(detail=True, methods=('post',))
    def shopping_cart(self, request, pk):
        return self.write_recipe_to(
            request, serializers.ShoppingCartSerializer, pk
        )

    @favorite.mapping.delete
    def delete_from_favorite(self, request, pk):
        return self.delete_recipe_from(request, Favourites, pk)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk):
        return self.delete_recipe_from(request, ShoppingCart, pk)

    @action(detail=False)
    def download_shopping_cart(self, request):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit'),
        ).annotate(
            amount=Coalesce(
                Sum('amount', output_field=IntegerField()), Value(0)
            )
        ).order_by('name')

        return HttpResponse(
            render_to_string(
                'api/shopping_cart.txt',
                {
                    'ingredients': ingredients,
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

    @action(detail=False)
    def subscriptions(self, request):
        """Action to retrieve the list of user subscriptions."""
        subscriptions = request.user.subscriptions.all()

        serializer = serializers.UserWithRecipesSerializer(
            self.paginate_queryset(subscriptions),
            many=True,
            context={'request': request}
        )

        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=('post',))
    def subscribe(self, request, pk):
        data = {
            'subscriber': request.user.id,
            'subscribtion': pk
        }
        serializer = serializers.SubscriptionsSerializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk):
        subscription = get_object_or_404(
            Subscriptions,
            subscriber=request.user.id,
            subscribtion=pk
        )
        subscription.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
