from django.urls import path
from .views import AvailableSlotsView, AppointmentCreateView, PaymentStartView, PaymentCallbackView, \
    AppointmentDetailView

urlpatterns = [
    path('slots/', AvailableSlotsView.as_view(), name='slots'),
    path('appointment/', AppointmentCreateView.as_view(), name='appointment_create'),
    path('appointment/<int:appointment_id>/', AppointmentDetailView.as_view(), name='appointment_detail'),
    path('payment/start/', PaymentStartView.as_view(), name='payment_start'),
    path('payment/callback/', PaymentCallbackView.as_view(), name='payment_callback'),
]