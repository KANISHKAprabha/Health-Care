from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from accounts.models import User


class UserAdmin(DjangoUserAdmin):
    model = User
    ordering = ["email"]
    list_display = ["email", "name", "is_staff", "is_active"]
    fieldsets = (
        (None, {"fields": ("email", "name", "password")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "name", "password1", "password2")}),
    )
    search_fields = ["email", "name"]
    filter_horizontal = ["groups", "user_permissions"]


admin.site.register(User, UserAdmin)
