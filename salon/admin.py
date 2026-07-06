from django.contrib import admin
from .models import Salon


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'owner', 'created_at', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'name_en', 'phone')
    readonly_fields = ('created_at', 'slug')