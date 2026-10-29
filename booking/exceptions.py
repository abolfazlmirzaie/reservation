class SlotUnavailableError(Exception):
    pass


class InactiveResourceError(Exception):
    pass


class PaymentStatusError(Exception):
    pass


class PaymentExpiresError(Exception):
    pass


class PaymentNotFoundError(Exception):
    pass


class PaymentVerificationError(Exception):
    pass


class AppointmentNotFoundError(Exception):
    pass


class UnAvailableStatusError(Exception):
    pass

class NameRequiredError(Exception):
    pass

class UnCancellableAppointmentError(Exception):
    pass