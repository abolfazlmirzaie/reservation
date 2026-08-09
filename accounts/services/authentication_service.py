from django.contrib.auth import get_user_model

from .otp_service import OTPService

User = get_user_model()


class AuthenticationService:
    @staticmethod
    def register_login(*, phone_number):

        otp = OTPService.generate_otp(phone_number)
