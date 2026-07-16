from django.shortcuts import render

from .models import Stylist
from .serializers import StylistServiceSerializer, StylistPublicSerializer
from rest_framework.generics import RetrieveAPIView



class StylistView(RetrieveAPIView):
    serializer_class = StylistPublicSerializer
    queryset = Stylist.objects.filter(is_active=True)
    lookup_field = 'slug'
