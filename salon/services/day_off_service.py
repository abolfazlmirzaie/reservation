from django.db import transaction
from salon.models import DayOff
from booking.models import Appointment


class DayOffService:
    @staticmethod
    @transaction.atomic
    def create_day_off(*, date, stylist, reason=""):

        day_off = DayOff.objects.create(
            date=date,
            stylist=stylist,
            reason=reason,
        )

        CANCELLABLE_APPOINTMENT_STATUSES = [
            "pending_payment",
            "confirmed",
        ]


        appointment = Appointment.objects.filter(
            stylist_service__stylist=stylist,
            start_time__date=date,
            status__in=CANCELLABLE_APPOINTMENT_STATUSES,
        )

        appointment.update(
            status="cancelled_by_stylist"
        )

        return day_off