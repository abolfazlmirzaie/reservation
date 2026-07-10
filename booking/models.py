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