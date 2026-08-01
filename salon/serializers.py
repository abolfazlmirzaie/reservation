from rest_framework import serializers
from .models import Stylist, StylistService
from booking.models import Appointment


class StylistServiceSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name')

    class Meta:
        model = StylistService
        fields = ['id', 'service_name', 'price', 'duration_minutes']




class StylistPublicSerializer(serializers.ModelSerializer):
    salon_name = serializers.CharField(source='salon.name')
    service = StylistServiceSerializer(source='services', many=True)

    class Meta:
        model = Stylist
        fields = ['name', 'salon_name', 'service']


class StylistAppointmentsQuerySerializer(serializers.Serializer):
    date = serializers.DateField(required=True)





class StylistAppointmentsSerializer(serializers.ModelSerializer):
    service = serializers.CharField(source='stylist_service.service.name')
    price = serializers.IntegerField(source='service_price_snapshot')
    deposit = serializers.IntegerField(source='deposit_amount')

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











