from django.db import models
from django.utils import timezone
from salon.models import StylistService







class Appointment(models.Model):
    STATUS_CHOICES = (
        ('pending_payment', 'در انتظار پرداخت'),
        ('confirmed', 'تایید شده'),
        ('cancelled_by_customer', 'لغو شده توسط مشتری'),
        ('cancelled_by_stylist', 'لغو شده توسظ ارایشگر'),
        ('completed', 'انجام شده'),
        ('no_show', 'عدم حضور مشتری'),
    )

    stylist_service = models.ForeignKey(StylistService, on_delete=models.PROTECT, related_name='appointments')
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=11)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_payment')


    service_price_snapshot = models.PositiveIntegerField()
    deposit_amount = models.PositiveIntegerField()
    platform_share = models.PositiveIntegerField()
    salon_share = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "نوبت"
        verbose_name_plural = "نوبت ها"


    def __str__(self):
        return f"{self.customer_name} - {self.stylist_service.stylist.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"



class PlatformSettings(models.Model):
    deposit_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    deposit_minimum = models.PositiveIntegerField(default=5000)
    deposit_maximum = models.PositiveIntegerField(default=20000)
    platform_share_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)
    
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