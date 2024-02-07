from django.contrib import admin
from django.utils.safestring import mark_safe

from recipes import models


class RecipeIngredientInline(admin.TabularInline):
    """Inline admin interface for managing ingredients within a recipe."""

    model = models.IngredientInRecipe
    extra = 0
    min_num = 1


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin interface for managing tags."""

    list_display = (
        'name',
        'slug',
        'color'
    )


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Admin interface for managing ingredients."""

    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Admin interface for managing recipes."""

    list_display = (
        'name',
        'author',
    )
    search_fields = (
        'name',
        'author__first_name',
        'author__last_name'
    )
    list_filter = ('tags',)
    inlines = (RecipeIngredientInline,)
    readonly_fields = ('total_favorites', 'ingredients_list')

    @admin.display(description='Добавлено в избранное')
    def total_favorites(self, obj):
        return obj.favourites.count()

    @admin.display(description='Список ингредиентов')
    def ingredients_list(self, obj):
        return ', '.join(
            [str(ingredient) for ingredient in obj.ingredient_in_recipe.all()]
        )

    @admin.display(description="Изображение")
    def image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" height="60">')
