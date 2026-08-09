from django.db import models
from django.utils.text import slugify

from accounts.models import User


class SalonCategory(models.TextChoices):
    MENS_SALON = "mens_salon", "آرایشگاه مردانه"
    WOMENS_SALON = "womens_salon", "آرایشگاه زنانه"


class Salon(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_salons"
    )
    name = models.CharField(max_length=100, verbose_name="نام سالن به فارسی")
    name_en = models.CharField(max_length=100, verbose_name="نام سالن به انگلیسی")
    category = models.CharField(max_length=20, choices=SalonCategory.choices)
    address = models.CharField(max_length=300)
    phone = models.CharField(max_length=10)
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name_en)
            slug = base_slug
            counter = 1
            while Salon.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Stylist(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="stylist_profile",
        null=True,
        blank=True,
    )
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name="stylists")
    name = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    phone = models.CharField(max_length=11)
    booking_window_days = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name_en)
            slug = base_slug
            counter = 1
            while Stylist.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}-{self.salon.name}"


class Service(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.salon.name}"


class StylistService(models.Model):
    stylist = models.ForeignKey(
        Stylist, on_delete=models.CASCADE, related_name="services"
    )
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="services_stylists"
    )
    price = models.PositiveIntegerField()
    duration_minutes = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["stylist", "service"],
                name="unique_stylists_service",
            )
        ]

    def __str__(self):
        return f"{self.stylist.name} - {self.service.name} - {self.price}"


class WorkingHours(models.Model):
    DAY_CHOICES = (
        (0, "شنبه"),
        (1, "یکشنبه"),
        (2, "دوشنبه"),
        (3, "سه‌شنبه"),
        (4, "چهارشنبه"),
        (5, "پنج‌شنبه"),
        (6, "جمعه"),
    )

    stylist = models.ForeignKey(
        Stylist, on_delete=models.CASCADE, related_name="working_hours"
    )
    day_of_week = models.PositiveIntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["stylist", "day_of_week"],
                name="unique_stylists_working_day",
            )
        ]
        verbose_name = "ساعت کاری"
        verbose_name_plural = "ساعات کاری"

    def __str__(self):
        return f"{self.stylist.name} - {self.get_day_of_week_display()}"


class DayOff(models.Model):
    stylist = models.ForeignKey(
        Stylist, on_delete=models.CASCADE, related_name="day_offs"
    )
    date = models.DateField()
    reason = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["stylist", "date"],
                name="unique_stylists_day_off",
            )
        ]

    def __str__(self):
        return f"{self.stylist.name} - {self.date}"
