from functools import cache

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission, IsAuthenticated
from salon.models import Stylist

User = get_user_model()


class IsStylistOrSalonOwner(BasePermission):
    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False
        slug = view.kwargs["slug"]
        stylist = get_object_or_404(Stylist, slug=slug)

        view.cached_stylist = stylist

        if request.user.role in (User.Role.STYLIST, User.Role.SALON_OWNER):
            if request.user.role == User.Role.STYLIST:
                if stylist.user == request.user:
                    return True
            elif request.user.role == User.Role.SALON_OWNER:
                if stylist.salon.owner == request.user:
                    return True
        return False


class IsCustomer(BasePermission):
    def has_permission(self, request, view):

        return request.user.is_authenticated and request.user.role == User.Role.CUSTOMER
