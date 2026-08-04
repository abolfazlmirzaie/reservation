from rest_framework import status
from rest_framework.response import Response
from .services.day_off_service import DayOffService
from .models import Stylist
from .serializers import StylistPublicSerializer, StylistAppointmentsQuerySerializer, StylistAppointmentsSerializer, \
    DayOffSerializer
from rest_framework.views import APIView
from booking.services.appointment_service import AppointmentService
from rest_framework.generics import RetrieveAPIView, get_object_or_404


class StylistView(RetrieveAPIView):
    serializer_class = StylistPublicSerializer
    queryset = Stylist.objects.filter(is_active=True)
    lookup_field = 'slug'



class StylistAppointmentsView(APIView):
    def get(self, request ,slug, *args, **kwargs):

        serializer = StylistAppointmentsQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        appointments = AppointmentService.get_stylist_appointments(
            stylist_slug=slug,
            target_date=serializer.validated_data['date'],
        )

        output_serializer = StylistAppointmentsSerializer(appointments, many=True)

        return Response(output_serializer.data)


class SetDayOffView(APIView):


    def post(self, request, slug, *args, **kwargs):

        serializer = DayOffSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        stylist = get_object_or_404(Stylist, slug=slug)

        day_off = DayOffService.create_day_off(
            stylist=stylist,
            date=serializer.validated_data['date'],
            reason=serializer.validated_data['reason'],
        )

        return Response(
            {
                "message" : "مرخصی ثبت شد",
                "day_off_id" : day_off.id,
            },
            status=status.HTTP_201_CREATED
        )