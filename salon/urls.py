from django.urls import path
from .views import StylistView




urlpatterns = [
    path('stylist/<slug:slug>/', StylistView.as_view(), name='stylist-detail'),
]