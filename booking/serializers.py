from rest_framework import serializers
from salon.models import StylistService




class AppointmentCreateSerializer(serializers.Serializer):
    stylist_service = serializers.PrimaryKeyRelatedField(queryset=StylistService.objects.all())
    date = serializers.DateField()
    time = serializers.TimeField()
    customer_name = serializers.CharField(max_length=100)
    customer_number = serializers.CharField(max_length=11)