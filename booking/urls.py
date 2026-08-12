from django.urls import path

from .views import (
    AppointmentCreateView,
    AppointmentDetailView,
    AppointmentUpdateView,
    AvailableSlotsView,
    PaymentCallbackView,
    PaymentStartView,
)

urlpatterns = [
    path("slots/", AvailableSlotsView.as_view(), name="slots"),
    path("appointment/create/", AppointmentCreateView.as_view(), name="appointment_create"),
    path(
        "appointment/<int:appointment_id>/",
        AppointmentDetailView.as_view(),
        name="appointment_detail",
    ),
    path(
        "appointment/<int:appointment_id>/status/",
        AppointmentUpdateView.as_view(),
        name="update_appointment_status",
    ),
    path("payment/start/", PaymentStartView.as_view(), name="payment_start"),
    path("payment/callback/", PaymentCallbackView.as_view(), name="payment_callback"),
]
