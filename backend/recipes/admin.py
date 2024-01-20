from django.contrib import admin

from recipes.models import (
    ArchivedIngredient, Ingredient, Recipe, RecipeIngredient, Tag
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'color'
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
    )
    exclude = ('is_archived',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_archived=False)


@admin.register(ArchivedIngredient)
class ArchivedIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient',
        'archived_at',
    )
    readonly_fields = ('ingredient',)
    actions = ('unarchive',)

    def unarchive(self, request, queryset):
        for archived_ingredient in queryset:
            archived_ingredient.unarchive()

    unarchive.short_description = 'Разархивировать'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'coocking_time',
        'pub_date'
    )
    inlines = (RecipeIngredientInline,)
