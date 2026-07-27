from booking.exceptions import PaymentExpiresError, PaymentStatusError
from booking.models import Payment
from django.db import transaction
from django.utils import timezone



class PaymentService:

    @staticmethod
    @transaction.atomic

    def start_payment(appointment):

        if appointment.status != 'pending_payment':
            raise PaymentStatusError(
                'این نوبت قابل پرداخت نیست'
            )

        if (
                appointment.expires_at is None
                or appointment.expires_at < timezone.now()
        ):
            raise PaymentExpiresError(
                'زمان پرداخت این نوبت به اتمام رسیده'
            )

        payment, created = Payment.objects.get_or_create(
            appointment=appointment,
            defaults={
                "amount": appointment.deposit_amount,
                "status": "pending",
            }
        )

        return {
            'payment': payment,
            'payment_url': "https://example.com/payment"
        }
