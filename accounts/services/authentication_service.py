from .otp_service import OTPService
from django.contrib.auth import get_user_model
User = get_user_model()



class AuthenticationService:


    @staticmethod
    def register_login(*, phone_number):

        otp = OTPService.generate_otp(phone_number)







