from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone_number = models.CharField(max_length=11, unique=True, blank=True, null=True)

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        STYLIST = "stylist", "Stylist"
        SALON_OWNER = "salon_owner", "Salon Owner"


    username = models.CharField(max_length=11, unique=True, blank=True, null=True)

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER
    )

    REQUIRED_FIELDS = []



    def __str__(self):
        return self.phone_number or f"User {self.pk}"



class OTPGenerator(models.Model):
    phone_number = models.CharField(max_length=11, unique=True, blank=True, null=True)
    code = models.CharField(max_length=6, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.phone_number

