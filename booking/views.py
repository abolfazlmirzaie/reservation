from datetime import datetime
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.permissions import (
    IsStylistOrSalonOwner,
    IsCustomer,
    CanManageAppointments,
)
from salon.models import StylistService

from .exceptions import (
    AppointmentNotFoundError,
    PaymentExpiresError,
    PaymentNotFoundError,
    PaymentStatusError,
    PaymentVerificationError,
    SlotUnavailableError,
    UnAvailableStatusError,
)
from .serializers import (
    AppointmentCreateSerializer,
    AppointmentDetailSerializer,
    AvailableSlotsSerializer,
    PaymentCallbackSerializer,
    PaymentStartSerializer,
    UpdateAppointmentSerializer,
)
from .services.appointment_service import AppointmentService
from .services.payment_service import PaymentService
from .services.slot_service import get_available_slots


class AvailableSlotsView(APIView):
    def get(self, request):
        serializer = AvailableSlotsSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        stylist_service_id = serializer.validated_data["stylist_service"]
        date_str = serializer.validated_data["date"]

        if not stylist_service_id or not date_str:
            return Response(
                {"error": "stylist_service_id and date are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            stylist_service = StylistService.objects.get(id=stylist_service_id)
        except StylistService.DoesNotExist:
            return Response(
                {"error": "this service for this stylist does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "invalid date format"}, status=status.HTTP_400_BAD_REQUEST
            )

        slots = get_available_slots(stylist_service, target_date)
        slot_strings = [slot.strftime("%H:%M") for slot in slots]
        return Response(
            {"available_slots": slot_strings},
        )


class AppointmentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = AppointmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        stylist_service = serializer.validated_data["stylist_service"]
        target_date = serializer.validated_data["date"]
        target_time = serializer.validated_data["time"]
        customer_name = serializer.validated_data["customer_name"]

        try:
            appointment = AppointmentService.create(
                stylist_service=stylist_service,
                target_date=target_date,
                target_time=target_time,
                customer_name=customer_name,
                customer_phone=request.user.phone_number,
            )
        except SlotUnavailableError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {
                "appointment_id": appointment.id,
                "deposit_amount": appointment.deposit_amount,
                "message": "نوبت شما ثبت شد. لطفاً برای تایید نهایی، بیعانه را پرداخت کنید",
            },
            status=status.HTTP_201_CREATED,
        )


class PaymentStartView(APIView):
    def post(self, request, *args, **kwargs):

        serializer = PaymentStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.validated_data["appointment"]

        try:
            result = PaymentService.start_payment(
                appointment=appointment,
            )

        except PaymentStatusError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except PaymentExpiresError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "payment_url": result["payment_url"],
                "payment_id": result["payment"].id,
            },
            status=status.HTTP_200_OK,
        )


class PaymentCallbackView(APIView):
    def get(self, request, *args, **kwargs):
        serializer = PaymentCallbackSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        authority = serializer.validated_data["Authority"]
        payment_status = serializer.validated_data["Status"]

        try:
            payment = PaymentService.verify_payment(
                authority=authority,
                status=payment_status,
            )

        except PaymentNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )

        except PaymentVerificationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": "پرداخت با موفقیت تایید شد.",
                "payment_id": payment.id,
            },
            status=status.HTTP_200_OK,
        )


class AppointmentDetailView(APIView):
    permission_classes = [IsStylistOrSalonOwner]

    def get(self, request, appointment_id, *args, **kwargs):

        try:
            appointment = AppointmentService.get_appointment(
                appointment_id=appointment_id
            )

        except AppointmentNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AppointmentDetailSerializer(appointment)

        return Response(serializer.data)


class AppointmentUpdateView(APIView):
    permission_classes = [IsStylistOrSalonOwner]

    def patch(self, request, appointment_id, *args, **kwargs):

        serializer = UpdateAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            AppointmentService.update_appointment(
                appointment_id=appointment_id,
                status=serializer.validated_data["status"],
            )

        except AppointmentNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )

        except UnAvailableStatusError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "وضعیت نوبت با موفقیت بروزرسانی شد."},
            status=status.HTTP_200_OK,
        )


class CancelAppointmentView(APIView):
    permission_classes = [CanManageAppointments]

    def post(self, request, appointment_id, *args, **kwargs):

        try:
            AppointmentService.cancel_appointment(
                appointment_id=appointment_id,
            )
        except AppointmentNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "message": "نوبت شما لغو شد بیعانه تا حداکثر 72 ساعت به حساب شما باز میگردد."
            },
            status=status.HTTP_200_OK,
        )
