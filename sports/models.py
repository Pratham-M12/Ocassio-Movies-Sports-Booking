from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model

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
    
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(SportsMatch, on_delete=models.CASCADE)
    bays = models.ManyToManyField(Bay)
    total_amount = models.PositiveIntegerField()
    payment_method = models.CharField(max_length=50)
    booking_time = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"{self.user.username} - {self.match.title}"