from django.urls import path

from .views import OTPVerifyView, RegisterOrLoginView

urlpatterns = [
    path("request-otp/", RegisterOrLoginView.as_view(), name="request-otp"),
    path("verify-otp/", OTPVerifyView.as_view(), name="verify-otp"),
]
