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
