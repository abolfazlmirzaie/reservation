from django.contrib import admin
from .models import Appointment, PlatformSettings


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'stylist_service', 'start_time', 'status')
    list_filter = ('status', 'stylist_service__stylist')
    search_fields = ('customer_name', 'customer_phone')



@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ('deposit_percentage', 'deposit_minimum', 'deposit_maximum', 'platform_share_percentage')

    def has_add_permission(self, request):
        return not PlatformSettings.objects.exists()