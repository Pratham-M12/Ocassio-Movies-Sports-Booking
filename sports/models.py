from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.crypto import get_random_string

User = get_user_model()

class SportsMatch(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    venue = models.CharField(max_length=200)
    date = models.DateField()
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to='sports/')
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Bay(models.Model):
    # link to match (or showtime if your architecture uses showtimes)
    match = models.ForeignKey(SportsMatch, related_name='bays', on_delete=models.CASCADE)
    code = models.CharField(max_length=50)      # e.g. "BAY A L1" or "VIP A1"
    stand = models.CharField(max_length=100)     # e.g. "North", "South", "Wing A"
    ring = models.IntegerField(default=0)        # 0 = ground, 1 = 1st, 2 = 2nd
    price = models.PositiveIntegerField(default=0)
    is_booked = models.BooleanField(default=False)
    extra_meta = models.JSONField(blank=True, null=True)  # optional

    class Meta:
        unique_together = ('match', 'code')

    def __str__(self):
        return f"{self.match.title} - {self.code}"
    
def generate_booking_ref():
    return get_random_string(12).upper()

class Booking(models.Model):
    """Stores confirmed sports bookings"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    match = models.ForeignKey('SportsMatch', on_delete=models.CASCADE)
    bay = models.ForeignKey('Bay', on_delete=models.SET_NULL, null=True, blank=True)
    booking_ref = models.CharField(max_length=20, unique=True)
    ticket_count = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    payment_method = models.CharField(max_length=50)
    booked_at = models.DateTimeField(auto_now_add=True)
    entry_gate = models.CharField(max_length=50, blank=True, null=True)
    seat_numbers = models.JSONField(default=list, blank=True)
    booking_ref = models.CharField(max_length=12, unique=True, default=generate_booking_ref, editable=False)

    def __str__(self):
        return f"{self.user.username} - {self.match.title} ({self.booking_ref})"
