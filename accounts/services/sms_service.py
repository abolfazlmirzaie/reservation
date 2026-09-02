from accounts.exceptions import FailedSendOTPError, FailedSendMassageError

class SmsService:

    @staticmethod
    def send_otp(phone_number, code):

        try:
            print(f"code:{code} sent to phone number:{phone_number}")
            return True
        except Exception as e:
            raise FailedSendOTPError(
                "failed to send otp please try again",
            )




    @staticmethod
    def send_sms(phone_number, text):
        try:
            print(f"text:{text} sent to phone number:{phone_number}")
            return True
        except Exception as e:
            raise FailedSendMassageError(
                "failed to send massage please try again",
            )