from django.urls import path
from .views import AvailableSlotsView, AppointmentCreateView, PaymentStartView, PaymentCallbackView

urlpatterns = [
    path('slots/', AvailableSlotsView.as_view(), name='slots'),
    path('appointment/', AppointmentCreateView.as_view(), name='appointment_create'),
    path('payment/start/', PaymentStartView.as_view(), name='payment_start'),
    path('payment/callback/', PaymentCallbackView.as_view(), name='payment_callback'),
]