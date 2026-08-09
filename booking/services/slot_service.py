from datetime import datetime, timedelta

from django.db.models import Q
from django.utils import timezone

from booking.models import Appointment
from salon.models import DayOff, WorkingHours


def get_django_day_of_week(python_weekday):

    mapping = {
        5: 0,
        6: 1,
        0: 2,
        1: 3,
        2: 4,
        3: 5,
        4: 6,
    }
    return mapping[python_weekday]


BUSY_APPOINTMENT_STATUSES = [
    "confirmed",
    "completed",
]


def get_available_slots(stylist_service, target_date, step_minutes=30):
    stylist = stylist_service.stylist
    duration = timedelta(minutes=stylist_service.duration_minutes)

    max_date = timezone.localdate() + timedelta(days=stylist.booking_window_days)
    if target_date > max_date or target_date < timezone.localdate():
        return []

    day_of_week = get_django_day_of_week(target_date.weekday())
    working_hours = WorkingHours.objects.filter(
        stylist=stylist, day_of_week=day_of_week, is_active=True
    ).first()

    if not working_hours:
        return []

    if DayOff.objects.filter(stylist=stylist, date=target_date).exists():
        return []

    step = timedelta(minutes=step_minutes)
    day_start = timezone.make_aware(
        datetime.combine(target_date, working_hours.start_time)
    )
    day_end = timezone.make_aware(datetime.combine(target_date, working_hours.end_time))

    booked_appointments = (
        Appointment.objects.filter(
            stylist_service__stylist=stylist,
            start_time__date=target_date,
        )
        .filter(
            Q(status__in=BUSY_APPOINTMENT_STATUSES)
            | Q(status="pending_payment", expires_at__gt=timezone.now())
        )
        .order_by("start_time")
    )

    booked_ranges = [
        (timezone.localtime(appt.start_time), timezone.localtime(appt.end_time))
        for appt in booked_appointments
    ]
    boundary_points = sorted(
        set(
            [day_start]
            + [timezone.localtime(appt.end_time) for appt in booked_appointments]
        )
    )

    available_slots = []
    for start_point in boundary_points:
        current = start_point
        while current + duration <= day_end:
            slot_end = current + duration
            has_conflict = any(
                current < booked_end and slot_end > booked_start
                for booked_start, booked_end in booked_ranges
            )
            if has_conflict:
                break
            available_slots.append(current.time())
            current += step

    return sorted(set(available_slots))
