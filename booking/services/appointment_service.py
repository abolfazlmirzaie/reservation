from datetime import datetime, timedelta

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from booking.exceptions import (
    AppointmentNotFoundError,
    InactiveResourceError,
    SlotUnavailableError,
    UnAvailableStatusError,
)
from booking.models import Appointment
from booking.services.deposit_service import calculate_deposit
from booking.services.slot_service import get_available_slots


class AppointmentService:
    @staticmethod
    def validate(stylist_service):

        if not stylist_service.stylist.salon.is_active:
            raise InactiveResourceError("این سالن در حال حاضر فعال نیست.")

        if not stylist_service.stylist.is_active:
            raise InactiveResourceError("این آرایشگر در حال حاضر فعال نیست.")

        if not stylist_service.service.is_active:
            raise InactiveResourceError("این خدمت در حال حاضر فعال نیست.")

    @staticmethod
    @transaction.atomic
    def create(
        *,
        stylist_service,
        target_date,
        target_time,
        customer_name,
        customer_phone,
    ):

        AppointmentService.validate(stylist_service)
        available_slots = get_available_slots(stylist_service, target_date)

        if target_time not in available_slots:
            raise SlotUnavailableError(
                "متاسفانه این ساعت قابل رزرو نیست. لطفاً ساعت دیگری انتخاب کنید."
            )

        deposit_data = calculate_deposit(stylist_service)

        start_datetime = timezone.make_aware(datetime.combine(target_date, target_time))

        end_datetime = start_datetime + timedelta(
            minutes=stylist_service.duration_minutes
        )

        appointment = Appointment.objects.create(
            stylist_service=stylist_service,
            customer_name=customer_name,
            customer_phone=customer_phone,
            start_time=start_datetime,
            end_time=end_datetime,
            status="pending_payment",
            expires_at=timezone.now() + timedelta(minutes=10),
            **deposit_data,
        )

        return appointment

    @staticmethod
    def get_stylist_appointments(*, stylist_slug, target_date):

        appointments = (
            Appointment.objects.select_related(
                "stylist_service",
                "stylist_service__service",
                "stylist_service__stylist",
            )
            .filter(
                stylist_service__stylist__slug=stylist_slug,
                start_time__date=target_date,
            )
            .order_by("start_time")
        )

        return appointments

    @staticmethod
    def get_appointment(*, appointment_id):

        try:
            appointment = Appointment.objects.select_related(
                "stylist_service",
                "stylist_service__service",
                "stylist_service__stylist",
            ).get(id=appointment_id)

        except Appointment.DoesNotExist:
            raise AppointmentNotFoundError("نوبت موردنظر پیدا نشد")
        return appointment

    @staticmethod
    def update_appointment(*, appointment_id, status):

        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            raise AppointmentNotFoundError("نوبت موردنظر پیدا نشد")

        allowed_status = [
            "cancelled_by_stylist",
            "completed",
            "no_show",
        ]

        if status not in allowed_status:
            raise UnAvailableStatusError(
                "وضعیت وارد شده معتبر نیست لطفا از این وضعیت ها استفاده کنید: completed, cancelled_by_stylist, no_show"
            )

        appointment.status = status
        appointment.save(update_fields=["status"])
