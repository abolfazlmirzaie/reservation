


UNAVAILABLE_SLOTS_STATUSES = [
            "pending_payment",
            "confirmed",
            "cancelled_by_stylist",
            "completed",
            "no_show",

        ]


ALLOWED_STATUSES_FOR_UPDATE_APPOINTMENT = [
            "cancelled_by_stylist",
            "completed",
            "no_show",
        ]

INVALID_STATUS_FOR_CANCEL_APPOINTMENT = [
            "pending_payment",
            "confirmed",
        ]