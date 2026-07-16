from rest_framework import serializers
from .models import Stylist, StylistService



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