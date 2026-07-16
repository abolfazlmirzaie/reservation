from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from salon.models import StylistService
from .services.booking_service import get_available_slots



class AvailableSlotsView(APIView):
    def get(self, request):
        stylist_service_id = request.query_params.get('stylist_service')
        date_str = request.query_params.get('date')

        if not stylist_service_id or not date_str:
            return Response(
                {'error' : 'stylist_service_id and date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            stylist_service = StylistService.objects.get(id=stylist_service_id)
        except StylistService.DoesNotExist:
            return Response(
                {'error' : 'this service for this stylist does not exist'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error' : 'invalid date format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        slots = get_available_slots(stylist_service, target_date)
        slot_strings = [slot.strftime('%H:%M') for slot in slots]
        return Response(
            {'available_slots': slot_strings},
        )