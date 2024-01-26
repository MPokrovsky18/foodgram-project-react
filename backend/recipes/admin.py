from django.contrib import admin

from recipes.models import (
    ArchivedIngredient, Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 0


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin interface customization for Tag model.

    List display includes name, slug, and color.

    Model: Tag
    """

    list_display = (
        'name',
        'slug',
        'color'
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Admin interface customization for Ingredient model.

    - List display includes name and measurement_unit.
    - Excludes is_archived from the form to avoid direct modification.

    Model: Ingredient
    """

    list_display = (
        'name',
        'measurement_unit',
    )
    exclude = ('is_archived',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_archived=False)


@admin.register(ArchivedIngredient)
class ArchivedIngredientAdmin(admin.ModelAdmin):
    """
    Admin interface customization for ArchivedIngredient model.

    - List display includes the original ingredient
    and the timestamp when it was archived.
    - Readonly fields include the ingredient,
    and there is an action to unarchive selected items.

    Model: ArchivedIngredient
    """

    list_display = (
        'ingredient',
        'archived_at',
    )
    readonly_fields = ('ingredient',)
    actions = ('unarchive',)

    def unarchive(self, request, queryset):
        """Unarchive selected ArchivedIngredient instances."""
        for archived_ingredient in queryset:
            archived_ingredient.unarchive()

    unarchive.short_description = 'Разархивировать'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Admin interface customization for Recipe model.

    - List display includes name, author, coocking_time, and pub_date.
    - Displays RecipeIngredient instances within the Recipe admin page.

    Model: Recipe
    """

    list_display = (
        'name',
        'author',
        'coocking_time',
        'pub_date'
    )
    inlines = (RecipeIngredientInline, RecipeTagInline)
