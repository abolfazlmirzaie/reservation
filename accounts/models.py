import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .utils import normalize_phone_number


class User(AbstractUser):
    phone_number = models.CharField(max_length=11, unique=True, blank=True, null=True)

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        STYLIST = "stylist", "Stylist"
        SALON_OWNER = "salon_owner", "Salon Owner"

    username = models.CharField(max_length=11, unique=True, blank=True, null=True)

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number or f"User {self.pk}"
    
    
    def save(self, *args, **kwargs):
        phone_number = normalize_phone_number(self.phone_number)
        self.phone_number = phone_number
        super().save(*args, **kwargs)


class OTPGenerator(models.Model):
    phone_number = models.CharField(max_length=11, unique=True, blank=True, null=True)
    code = models.CharField(max_length=64, blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.expires_at = timezone.now() + datetime.timedelta(minutes=5)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.phone_number



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=20, blank=True, null=True)
    last_name = models.CharField(max_length=20, blank=True, null=True)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

