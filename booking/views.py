from .exceptions import SlotUnavailableError
from .serializers import AppointmentCreateSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from salon.models import StylistService
from .services.slot_service import get_available_slots
from booking.services.appointment_service import AppointmentService


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

        try:
            appointment = AppointmentService.create(
                stylist_service=stylist_service,
                target_date=target_date,
                target_time=target_time,
                customer_name=customer_name,
                customer_phone=customer_number,
            )
        except SlotUnavailableError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_409_CONFLICT,
            )


        return Response(
            {
                'appointment_id': appointment.id,
                'deposit_amount': appointment.deposit_amount,
                'message' : 'نوبت شما ثبت شد. لطفاً برای تایید نهایی، بیعانه را پرداخت کنید'
            },
            status=status.HTTP_201_CREATED
        )


