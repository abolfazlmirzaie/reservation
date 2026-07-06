from django.contrib import admin
from .models import Salon, Stylist




class StylistInline(admin.StackedInline):
    model = Stylist
    extra = 1
    readonly_fields = ('created_at', 'slug')

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'owner', 'created_at', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'name_en', 'phone')
    readonly_fields = ('created_at', 'slug')
    inlines = [StylistInline,]
