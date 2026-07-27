from rest_framework import serializers
from salon.models import StylistService
from .models import Appointment



class AppointmentCreateSerializer(serializers.Serializer):
    stylist_service = serializers.PrimaryKeyRelatedField(queryset=StylistService.objects.all())
    date = serializers.DateField()
    time = serializers.TimeField()
    customer_name = serializers.CharField(max_length=100)
    customer_number = serializers.CharField(max_length=11)







class PaymentStartSerializer(serializers.Serializer):
    appointment = serializers.IntegerField()

    def validate_appointment(self,value):
        try:
            appointment = Appointment.objects.get(id=value)
        except Appointment.DoesNotExist:
            raise serializers.ValidationError("نوبت پیدا نشد.")
        return appointment




class PaymentCallbackSerializer(serializers.Serializer):
    Authority = serializers.CharField(max_length=100)
    Status = serializers.CharField(max_length=20)


