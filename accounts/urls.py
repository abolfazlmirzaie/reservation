from django.urls import path

from .views import OTPVerifyView, RegisterOrLoginView, ProfileAPIView

urlpatterns = [
    path("request-otp/", RegisterOrLoginView.as_view(), name="request-otp"),
    path("verify-otp/", OTPVerifyView.as_view(), name="verify-otp"),
    path("profile/", ProfileAPIView.as_view(), name="profile"),
]
