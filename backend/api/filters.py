from django_filters.rest_framework import (
    CharFilter, FilterSet, NumberFilter, ModelMultipleChoiceFilter
)

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    """FilterSet for the Ingredient model, allowing filtering by name."""

    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """
    FilterSet for the Recipe model.

    Attributes:
    - is_favorited:
        Filters recipes by favorited status,
        requires a numerical value (1 for favorited).
    - is_in_shopping_cart:
        Filters recipes by shopping cart inclusion,
        requires a numerical value (1 for in shopping cart).
    - author: Filters recipes by author's user ID.
    - tags: Filters recipes by tags, allowing multiple values.
    """

    is_favorited = NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = NumberFilter(method='filter_is_in_shopping_cart')
    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        to_field_name='slug',
        field_name='tags__slug',
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        current_user = self.request.user

        if current_user.is_authenticated and value:
            return queryset.filter(favourites__user=current_user)

        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        current_user = self.request.user

        if current_user.is_authenticated and value:
            return queryset.filter(shopping_cart__user=current_user)

        return queryset
