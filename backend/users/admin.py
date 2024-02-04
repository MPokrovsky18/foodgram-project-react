from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from users.models import FoodgramUser

admin.site.unregister(Group)


@admin.register(FoodgramUser)
class FoodgramUserAdmin(UserAdmin):
    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
    )
    search_fields = (
        'email',
        'first_name',
        'last_name',
    )
    readonly_fields = ('all_recipes', 'all_subscribers')

    @admin.display(description='Количество рецептов')
    def all_recipes(self, obj):
        return obj.recipes.count()

    @admin.display(description='Количество подписчиков')
    def all_subscribers(self, obj):
        return obj.subscribers.count()
