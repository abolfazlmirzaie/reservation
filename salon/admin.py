from django.contrib import admin
from .models import Salon, Stylist, StylistService, Service


class StylistServiceInline(admin.TabularInline):
    model = StylistService
    extra = 1




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




@admin.register(Stylist)
class StylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'salon', 'is_active', 'booking_window_days')
    list_filter = ('salon', 'is_active')
    search_fields = ('name', 'name_en', 'phone')
    readonly_fields = ('created_at', 'slug')
    inlines = [StylistServiceInline,]



@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'salon', 'is_active')
    list_filter = ('salon', 'is_active')
    search_fields = ('name',)
























