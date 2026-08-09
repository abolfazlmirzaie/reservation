from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model


User = get_user_model()

class CanManageStylist(BasePermission):
    """
    Stylist:
        فقط Stylist خودش

    Salon Owner:
        Stylistهای سالن خودش
    """

    message = "You do not have permission to manage this stylist."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in (
                User.Role.STYLIST,
                User.Role.SALON_OWNER,
            )
        )

    def has_object_permission(self, request, view, stylist):

        # Stylist فقط خودش
        if request.user.role == User.Role.STYLIST:
            return stylist.user == request.user

        # Salon Owner فقط Stylistهای سالن خودش
        if request.user.role == User.Role.SALON_OWNER:
            return stylist.salon.owner == request.user

        return False



class CanManageAppointment(BasePermission):
    """
    Stylist:
        فقط Appointmentهای خودش

    Salon Owner:
        Appointmentهای Stylistهای سالن خودش
    """

    message = "You do not have permission to manage this appointment."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in (
                User.Role.STYLIST,
                User.Role.SALON_OWNER,
            )
        )

    def has_object_permission(self, request, view, appointment):

        stylist = appointment.stylist_service.stylist

        # Stylist فقط نوبت‌های خودش
        if request.user.role == User.Role.STYLIST:
            return stylist.user == request.user

        # Salon Owner نوبت‌های Stylistهای سالن خودش
        if request.user.role == User.Role.SALON_OWNER:
            return stylist.salon.owner == request.user

        return False







class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.role == "customer"
        )





