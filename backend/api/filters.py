from django_filters.rest_framework import FilterSet, CharFilter, NumberFilter

from recipes.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    """FilterSet for the Ingredient model, allowing filtering by name."""

    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = []


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
    author = NumberFilter(field_name='author__id')
    tags = CharFilter(method='filter_tags')

    class Meta:
        model = Recipe
        fields = []

    def filter_is_favorited(self, queryset, name, value):
        current_user = self.request.user

        if current_user.is_authenticated and value == 1:
            return queryset.filter(favorited_by=current_user)

        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        current_user = self.request.user

        if current_user.is_authenticated:
            if value == 1:
                return queryset.filter(added_to_shopping_list_by=current_user)

        return queryset

    def filter_tags(self, queryset, name, value):
        return queryset.filter(
            tags__slug__in=self.data.getlist(name)
        ).distinct()
