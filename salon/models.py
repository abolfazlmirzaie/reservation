from django.db import models
from accounts.models import User
from django.utils.text import slugify

class SalonCategory(models.TextChoices):
    MENS_SALON = 'mens_salon', 'آرایشگاه مردانه'
    WOMENS_SALON = 'womens_salon', 'آرایشگاه زنانه'


class Salon(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name="نام سالن به فارسی")
    name_en = models.CharField(max_length=100, verbose_name="نام سالن به انگلیسی")
    category = models.CharField(
        max_length=20,
        choices=SalonCategory.choices
    )
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
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name






class Stylist(models.Model):
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, related_name='staylists')
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
            while Salon.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}-{self.salon.name}"























