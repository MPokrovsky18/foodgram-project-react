from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from users.models import FoodgramUser

admin.site.unregister(Group)

UserAdmin.fieldsets += (
    ('Списки рецептов', {'fields': ('favorite_recipes', 'shopping_list')}),
    ('Подписки', {'fields': ('subscriptions',)}),
)


@admin.register(FoodgramUser)
class FoodgramUserAdmin(UserAdmin):
    """
    Admin interface customization for FoodgramUser model.

    List display includes:
        email, username, first name, last name, is_staff, and is_active.

    Fieldsets include the default UserAdmin fieldsets
    and additional fields for favorite_recipes and shopping_list.
    """

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
