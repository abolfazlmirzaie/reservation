from django.db import models

from salon.models import StylistService


class Appointment(models.Model):
    STATUS_CHOICES = (
        ("pending_payment", "در انتظار پرداخت"),
        ("confirmed", "تایید شده"),
        ("cancelled_by_customer", "لغو شده توسط مشتری"),
        ("cancelled_by_stylist", "لغو شده توسظ ارایشگر"),
        ("completed", "انجام شده"),
        ("no_show", "عدم حضور مشتری"),
    )

    stylist_service = models.ForeignKey(
        StylistService, on_delete=models.PROTECT, related_name="appointments"
    )
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=11)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default="pending_payment"
    )

    service_price_snapshot = models.PositiveIntegerField()
    deposit_amount = models.PositiveIntegerField()
    platform_share = models.PositiveIntegerField()
    salon_share = models.PositiveIntegerField()
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "نوبت"
        verbose_name_plural = "نوبت ها"

    def __str__(self):
        return f"{self.customer_name} - {self.stylist_service.stylist.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class PlatformSettings(models.Model):
    deposit_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=15.00
    )
    deposit_minimum = models.PositiveIntegerField(default=5000)
    deposit_maximum = models.PositiveIntegerField(default=20000)
    platform_share_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=20.00
    )

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    class Meta:
        verbose_name = "تنظیمات پلتفرم"
        verbose_name_plural = "تنظیمات پلتفرم"

    def __str__(self):
        return "تنظیمات پلتفرم"


class Payment(models.Model):
    STATUS_CHOICES = (
        ("pending", "در انتظار پرداخت"),
        ("success", "موفق"),
        ("failed", "ناموفق"),
        ("returned", "بازگشت داده شده"),
    )

    appointment = models.OneToOneField(
        Appointment, on_delete=models.PROTECT, related_name="payment"
    )
    amount = models.PositiveIntegerField()
    gateway_ref_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    authority = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
    )
    card_pan = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"

    def __str__(self):
        return f"{self.appointment.customer_name} - {self.amount} - {self.status}"


class SMSLog(models.Model):
    TYPE_CHOICES = (
        ("booking_confirmation", "تایید رزرو"),
        ("reminder", "یادآوری"),
        ("cancellation_by_salon", "لغو توسط سالن"),
        ("cancellation_by_customer", "لغو توسط مشتری"),
    )

    STATUS_CHOICES = (
        ("sent", "ارسال شده"),
        ("failed", "ناموفق"),
    )

    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, related_name="sms_logs"
    )
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="sent")
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "پیامک"
        verbose_name_plural = "پیامک‌ها"

    def __str__(self):
        return f"{self.appointment.customer_name} - {self.type} - {self.sent_at.strftime('%Y-%m-%d %H:%M')}"
