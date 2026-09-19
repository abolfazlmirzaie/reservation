from rest_framework import serializers

from salon.models import StylistService

from .models import Appointment


class AvailableSlotsSerializer(serializers.Serializer):
    stylist_service = serializers.IntegerField()
    date = serializers.CharField()


class AppointmentCreateSerializer(serializers.Serializer):
    stylist_service = serializers.PrimaryKeyRelatedField(
        queryset=StylistService.objects.all()
    )
    date = serializers.DateField()
    time = serializers.TimeField()
    customer_name = serializers.CharField(max_length=100, required=False, allow_blank=True)


    def validate(self, attrs):
        user = self.context['request'].user
        full_name = getattr(user.profile, "full_name", None)
        if full_name:
            attrs["customer_name"] = full_name
        elif not attrs["customer_name"]:
            raise serializers.ValidationError(
                {
                    "customer_name": "لطفاً نام و نام خانوادگی را وارد کنید."
                }
            )
        return attrs



class PaymentStartSerializer(serializers.Serializer):
    appointment = serializers.IntegerField()

    def validate_appointment(self, value):
        try:
            appointment = Appointment.objects.get(id=value)
        except Appointment.DoesNotExist:
            raise serializers.ValidationError("نوبت پیدا نشد.")
        return appointment


class PaymentCallbackSerializer(serializers.Serializer):
    Authority = serializers.CharField(max_length=100)
    Status = serializers.CharField(max_length=20)


class AppointmentDetailSerializer(serializers.ModelSerializer):
    service = serializers.CharField(source="stylist_service.service.name")
    stylist = serializers.CharField(source="stylist_service.stylist.name")

    class Meta:
        model = Appointment
        fields = [
            "id",
            "customer_name",
            "customer_phone",
            "service",
            "stylist",
            "service_price_snapshot",
            "deposit_amount",
            "start_time",
            "end_time",
            "status",
            "created_at",
        ]


class UpdateAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["status"]