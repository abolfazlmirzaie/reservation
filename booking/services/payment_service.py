from django.db import transaction
from django.utils import timezone
from django.utils.timezone import localtime

from accounts.services.sms_service import SmsService
from booking.exceptions import (
    PaymentExpiresError,
    PaymentNotFoundError,
    PaymentStatusError,
    PaymentVerificationError,
)
from booking.models import Payment, Appointment, SMSLog
from accounts.exceptions import FailedSendMassageError


class PaymentService:
    @staticmethod
    @transaction.atomic
    def start_payment(appointment):

        if appointment.status != "pending_payment":
            raise PaymentStatusError("این نوبت قابل پرداخت نیست")

        if appointment.expires_at is None or appointment.expires_at < timezone.now():
            raise PaymentExpiresError("زمان پرداخت این نوبت به اتمام رسیده")

        payment, created = Payment.objects.get_or_create(
            appointment=appointment,
            defaults={
                "amount": appointment.deposit_amount,
                "status": "pending",
            },
        )

        return {"payment": payment, "payment_url": "https://example.com/payment"}

    @staticmethod
    @transaction.atomic
    def verify_payment(*, authority, status):

        try:
            payment = Payment.objects.select_related("appointment").get(
                authority=authority
            )

        except Payment.DoesNotExist:
            raise PaymentNotFoundError("پرداخت موردنظر پیدا نشد.")

        if status != "OK":
            payment.status = "failed"
            payment.save(update_fields=["status"])
            raise PaymentVerificationError("پرداخت توسط کاربر لغو شد.")
        # TODO:
        # Verify payment with ZarinPal
        #
        # payment.status = "success"
        # payment.paid_at = timezone.now()
        # payment.save(update_fields=['status',
        #                             'paid_at'
        #                ]
        #              )
        #
        # appointment = payment.appointment
        # appointment.status = "confirmed"
        # appointment.save(update_fields=['status'])

        text = f"نوبت شما با موفقیت پرداخت شد. ساعت مراجعه : {localtime(payment.appointment.start_time).strftime('%m/%d %H:%M')} "

        try:
            SmsService.send_sms(payment.appointment.customer_phone, text)

            SMSLog.objects.create(
                type="booking_confirmation",
                status="sent",
                appointment=payment.appointment,
            )

        except FailedSendMassageError:
            SMSLog.objects.create(
                type="booking_confirmation",
                status="failed",
                appointment=payment.appointment,
            )

        return payment
