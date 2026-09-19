import hashlib
import random
from datetime import timedelta
from django.utils import timezone
from accounts.models import OTPGenerator


class OTPService:
    @staticmethod
    def generate_otp(phone_number):
        # ساخت کد تصادفی ۵ رقمی
        code = str(random.randint(10000, 99999))
        hash_code = hashlib.sha256(code.encode('utf-8')).hexdigest()
        expires_at = timezone.now() + timedelta(minutes=10)
        
        OTPGenerator.objects.update_or_create(
            phone_number=phone_number,
            defaults={
                "expires_at": expires_at,
                "code": hash_code,
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

        hash_code = hashlib.sha256(str(code).encode('utf-8')).hexdigest()

        if hash_code != otp.code:
            return False, "the code is wrong"

        otp.delete()
        return True, None
