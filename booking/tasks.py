from celery import shared_task
from django.utils import timezone

from .models import Appointment


@shared_task
def expire_pending_appointments():

    Appointment.objects.filter(
        status="pending_payment",
        expires_at__lte=timezone.now(),
    ).update(
        status="expired",
    )