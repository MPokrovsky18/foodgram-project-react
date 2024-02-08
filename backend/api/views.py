from django.contrib.auth import get_user_model
from django.db.models import Exists, F, Sum, Value, IntegerField, OuterRef
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api import serializers
from api.filters import IngredientFilter, RecipeFilter
from api.shopping_cart_renderer import render_shopping_cart_as_txt
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
                        user=self.request.user
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        recipe=OuterRef('pk'),
                        user=self.request.user
                    )
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
        get_object_or_404(Recipe, id=pk)
        target_to_delete = source_model.objects.filter(
            recipe=pk,
            user=request.user
        )

        if target_to_delete:
            target_to_delete.delete()

            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            status=status.HTTP_400_BAD_REQUEST
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

        return render_shopping_cart_as_txt(request.user, ingredients)


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
        authors = get_user_model().objects.filter(
            subscribers__subscriber=request.user
        )
        serializer = serializers.UserWithRecipesSerializer(
            self.paginate_queryset(authors),
            many=True,
            context={'request': request}
        )

        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=('post',))
    def subscribe(self, request, id):
        get_object_or_404(get_user_model(), id=id)
        data = {
            'subscriber': request.user.id,
            'author': id
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
    def unsubscribe(self, request, id):
        get_object_or_404(get_user_model(), id=id)
        target_to_delete = Subscriptions.objects.filter(
            author=id,
            subscriber=request.user
        )

        if target_to_delete:
            target_to_delete.delete()

            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            status=status.HTTP_400_BAD_REQUEST
        )
