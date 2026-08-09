from rest_framework import serializers

from booking.models import Appointment

from .models import DayOff, Stylist, StylistService, WorkingHours


class WorkingHoursSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(
        source="get_day_of_week_display",
        read_only=True,
    )

    class Meta:
        model = WorkingHours
        fields = [
            "day_of_week",
            "day_name",
            "start_time",
            "end_time",
        ]


class DayOffSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayOff
        fields = [
            "date",
            "reason",
        ]


class StylistServiceSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name")

    class Meta:
        model = StylistService
        fields = ["id", "service_name", "price", "duration_minutes"]


class StylistPublicSerializer(serializers.ModelSerializer):
    salon_name = serializers.CharField(source="salon.name")

    services = StylistServiceSerializer(
        many=True,
        read_only=True,
    )

    working_hours = WorkingHoursSerializer(
        many=True,
        read_only=True,
    )

    day_offs = DayOffSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Stylist
        fields = [
            "name",
            "salon_name",
            "booking_window_days",
            "services",
            "working_hours",
            "day_offs",
        ]


class StylistAppointmentsQuerySerializer(serializers.Serializer):
    date = serializers.DateField(required=True)


class StylistAppointmentsSerializer(serializers.ModelSerializer):
    service = serializers.CharField(source="stylist_service.service.name")
    price = serializers.IntegerField(source="service_price_snapshot")
    deposit = serializers.IntegerField(source="deposit_amount")

    class Meta:
        model = Appointment
        fields = [
            "id",
            "customer_name",
            "customer_phone",
            "service",
            "price",
            "deposit",
            "start_time",
            "end_time",
            "status",
        ]


class DayOffCreateSerializer(serializers.Serializer):
    date = serializers.DateField(required=True)
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=20,
    )
