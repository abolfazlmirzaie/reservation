from datetime import datetime, timedelta
from django.utils import timezone
from salon.models import WorkingHours, DayOff
from booking.models import Appointment

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