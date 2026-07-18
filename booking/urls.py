from django.urls import path
from .views import AvailableSlotsView, AppointmentCreateView

urlpatterns = [
    path('available-slots/', AvailableSlotsView.as_view(), name='available_slots'),
    path('appointment/', AppointmentCreateView.as_view(), name='appointment_create'),
]