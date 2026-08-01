from django.urls import path
from .views import StylistView, StylistAppointmentsView

urlpatterns = [
    path('stylist/<slug:slug>/', StylistView.as_view(), name='stylist-detail'),
    path('stylist/<slug:slug>/appointments/', StylistAppointmentsView.as_view(), name='stylist-appointments'),
]