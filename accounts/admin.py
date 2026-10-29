from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Profile

class UserAdmin(BaseUserAdmin):
    ordering = ("phone_number",)
    list_display = ("phone_number", "role", "is_staff", "is_active")
    search_fields = ("phone_number", "email")

    fieldsets = (
        (None, {
            "fields": ("phone_number", "password"),
        }),
        ("Personal info", {
            "fields": ("first_name", "last_name", "email"),
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
        ("Additional info", {
            "fields": ("role",),
        }),
        ("Important dates", {
            "fields": ("last_login", "date_joined"),
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "password1", "password2"),
        }),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Profile)
