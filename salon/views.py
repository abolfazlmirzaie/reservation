from django.db.models import Prefetch
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from accounts.permissions import IsStylistOrSalonOwner
from booking.services.appointment_service import AppointmentService

from .exceptions import DateError
from .models import DayOff, Stylist, StylistService, WorkingHours, Salon
from .serializers import (
    DayOffCreateSerializer,
    StylistAppointmentsQuerySerializer,
    StylistAppointmentsSerializer,
    StylistPublicSerializer,
    SalonSerializer,
    SalonDetailSerializer,
)
from .services.day_off_service import DayOffService

from .paginations import SalonPageNumberPagination


class StylistView(RetrieveAPIView):
    serializer_class = StylistPublicSerializer
    lookup_field = "slug"

    queryset = (
        Stylist.objects.filter(is_active=True)
        .select_related("salon")
        .prefetch_related(
            Prefetch(
                "services", queryset=StylistService.objects.select_related("service")
            ),
            Prefetch(
                "working_hours",
                queryset=WorkingHours.objects.filter(is_active=True).order_by(
                    "day_of_week"
                ),
            ),
            Prefetch(
                "day_offs",
                queryset=DayOff.objects.filter(date__gte=timezone.localdate()).order_by(
                    "date"
                ),
            ),
        )
    )


class StylistAppointmentsView(APIView):
    permission_classes = [IsStylistOrSalonOwner]

    def get(self, request, slug, *args, **kwargs):

        serializer = StylistAppointmentsQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        appointments = AppointmentService.get_stylist_appointments(
            stylist_slug=slug,
            target_date=serializer.validated_data["date"],
        )


        output_serializer = StylistAppointmentsSerializer(appointments, many=True)

        return Response(output_serializer.data)


class SetDayOffView(APIView):
    permission_classes = [IsStylistOrSalonOwner]


    def post(self, request, slug, *args, **kwargs):

        serializer = DayOffCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        stylist = get_object_or_404(Stylist, slug=slug)

        try:
            day_off = DayOffService.create_day_off(
                stylist=stylist,
                date=serializer.validated_data["date"],
                reason=serializer.validated_data["reason"],
            )
        except DateError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": "مرخصی ثبت شد",
                "day_off_id": day_off.id,
            },
            status=status.HTTP_201_CREATED,
        )


class SalonListView(ListAPIView):
    pagination_class = SalonPageNumberPagination
    permission_classes = [AllowAny]

    serializer_class = SalonSerializer
    queryset = Salon.objects.all()


class SalonDetailView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = SalonDetailSerializer
    lookup_field = "slug"

    queryset = Salon.objects.filter(is_active=True).prefetch_related(
        Prefetch(
            "stylists",
            queryset=(
                Stylist.objects.filter(is_active=True)
                .select_related("salon")
            ),
        )
    )
