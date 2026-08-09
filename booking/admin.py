from django.contrib import admin

from .models import Appointment, Payment, PlatformSettings, SMSLog


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "stylist_service", "start_time", "status")
    list_filter = ("status", "stylist_service__stylist")
    search_fields = ("customer_name", "customer_phone")


@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "deposit_percentage",
        "deposit_minimum",
        "deposit_maximum",
        "platform_share_percentage",
    )

    def has_add_permission(self, request):
        return not PlatformSettings.objects.exists()


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("appointment", "amount", "status", "paid_at")
    list_filter = ("status",)
    search_fields = ("appointment__customer_name", "gateway_ref_id")
    readonly_fields = ("created_at",)


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    list_display = ("appointment", "type", "status", "sent_at")
    list_filter = ("type", "status")
    search_fields = ("appointment__customer_name",)
    readonly_fields = ("sent_at",)
