from rest_framework.generics import CreateAPIView

from .models import Appointment
from .serializers import AppointmentCreateSerializer
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from salon.models import StylistService
from .services.booking_service import get_available_slots, calculate_deposit



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


class AppointmentCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = AppointmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        stylist_service = serializer.validated_data['stylist_service']
        target_date = serializer.validated_data['date']
        target_time = serializer.validated_data['time']
        customer_name = serializer.validated_data['customer_name']
        customer_number = serializer.validated_data['customer_number']

        available_slots = get_available_slots(stylist_service, target_date)
        if target_time not in available_slots:
            return Response(
                {'error' : 'متاسفانه این ساعت همین الان رزرو شد. لطفاً ساعت دیگری انتخاب کنید'},
                status=status.HTTP_409_CONFLICT
            )
        financials = calculate_deposit(stylist_service)

        start_datetime = timezone.make_aware(datetime.combine(target_date, target_time))
        end_datetime = start_datetime + timezone.timedelta(minutes=stylist_service.duration_minutes)

        appointment = Appointment.objects.create(
            stylist_service=stylist_service,
            customer_name=customer_name,
            customer_phone=customer_number,
            start_time=start_datetime,
            end_time=end_datetime,
            status='pending_payment',
            **financials
        )

        return Response(
            {
                'appointment_id': appointment.id,
                'deposit_amount': appointment.deposit_amount,
                'message' : 'نوبت شما ثبت شد. لطفاً برای تایید نهایی، بیعانه را پرداخت کنید'
            },
            status=status.HTTP_201_CREATED
        )
























