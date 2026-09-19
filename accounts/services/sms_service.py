import requests
from django.conf import settings
from melipayamak import Api

from accounts.exceptions import FailedSendOTPError, FailedSendMassageError


class SmsService:
    """
    SMS_BACKEND در settings.py دو مقدار می‌پذیرد:
      - "fake": فقط پیامک را در کنسول چاپ می‌کند (پیش‌فرض، برای توسعه محلی)
      - "melipayamak": با وب‌سرویس واقعی ملی‌پیامک ارسال می‌کند
    """

    @staticmethod
    def _get_client():
        api = Api(settings.MELIPAYAMAK_USERNAME, settings.MELIPAYAMAK_PASSWORD)
        return api.sms()

    @staticmethod
    def send_otp(phone_number):
        """
        برخلاف بقیه‌ی متدها، این متد کد را از بیرون نمی‌گیرد -
        ملی‌پیامک خودش کد OTP را تولید می‌کند و برمی‌گرداند.
        خروجی: رشته‌ی کد تولیدشده (که باید توسط OTPService ذخیره شود
        تا بعداً بتوان با آن verify کرد).
        """
        if settings.SMS_BACKEND == "fake":
            fake_code = "12345"
            print(f"code:{fake_code} sent to phone number:{phone_number}")
          
            return fake_code

        try:
            response = requests.post(
                f"https://console.melipayamak.com/api/send/otp/{settings.MELIPAYAMAK_OTP_TOKEN}",
                json={"to": phone_number},
                timeout=10,
            )
            data = response.json()
        except (requests.RequestException, ValueError) as e:
            raise FailedSendOTPError("failed to send otp please try again") from e

        # طبق مستندات، در صورت خطا فقط status پر می‌شود و code خالی است
        if not data.get("code"):
            raise FailedSendOTPError(data.get("status", "failed to send otp"))

        return data["code"]

    @staticmethod
    def send_sms(phone_number, text):
        if settings.SMS_BACKEND == "fake":
            print(f"text:{text} sent to phone number:{phone_number}")
            return True

        try:
            sms = SmsService._get_client()
            result = sms.send(
                phone_number,
                settings.MELIPAYAMAK_SENDER_NUMBER,
                text,
            )
            return SmsService._check_result(result)
        except Exception as e:
            raise FailedSendMassageError("failed to send sms") from e

    @staticmethod
    def _check_result(result):
        """
        ملی‌پیامک برای خطاها یک عدد منفی برمی‌گرداند (نه یک exception).
        این متد آن را به یک نتیجه‌ی boolean قابل‌فهم برای بقیه‌ی کد تبدیل می‌کند.
        """
        try:
            value = int(result)
        except (TypeError, ValueError):
            # پاسخ عددی نبود؛ فرض بر ارسال موفق (بسته به فرمت واقعی پاسخ ممکن است نیاز به اصلاح داشته باشد)
            return True

        if value < 0:
            return False
        return True