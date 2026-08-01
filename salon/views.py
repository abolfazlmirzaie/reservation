from rest_framework.response import Response

from .models import Stylist
from .serializers import StylistPublicSerializer, StylistAppointmentsQuerySerializer, StylistAppointmentsSerializer
from rest_framework.views import APIView
from booking.services.appointment_service import AppointmentService
from rest_framework.generics import RetrieveAPIView

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