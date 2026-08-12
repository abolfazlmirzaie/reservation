import random
from datetime import timedelta

from django.utils import timezone

from accounts.models import OTPGenerator


class OTPService:
    @staticmethod
    def generate_otp(phone_number):
        code = str(random.randint(10000, 99999))
        expires_at = timezone.now() + timedelta(minutes=10)
        OTPGenerator.objects.update_or_create(
            phone_number=phone_number,
            defaults={
                "expires_at": expires_at,
                "code": code,
            },
        )
        return code

    @staticmethod
    def verify_otp(phone_number, code):
        try:
            otp = OTPGenerator.objects.get(phone_number=phone_number)
        except OTPGenerator.DoesNotExist:
            return False, "there is no code for this number"

        if otp.expires_at < timezone.now():
            return False, "the code is expired"

        if otp.code != code:
            return False, "the code is invalid"

        return True, None

    @staticmethod
    def delete_otp(phone_number):
        otp = OTPGenerator.objects.filter(phone_number=phone_number).delete()
