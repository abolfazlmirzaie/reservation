from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'stylist_service', 'start_time', 'status')
    list_filter = ('status', 'stylist_service__stylist')
    search_fields = ('customer_name', 'customer_phone')