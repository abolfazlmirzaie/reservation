from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Profile


class UserAdmin(BaseUserAdmin):
    BaseUserAdmin.fieldsets += (("phone_info", {"fields": ("phone_number",)}),)
    list_display = ("email", "phone_number", "is_staff")


admin.site.register(User, UserAdmin)
admin.site.register(Profile)