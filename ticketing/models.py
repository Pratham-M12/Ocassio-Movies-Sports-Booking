import uuid
import qrcode
from io import BytesIO
from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from events.models import Event

class Ticket(models.Model):
    ticket_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    is_checked_in = models.BooleanField(default=False) #Track attendance
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)

    def __str__(self):
        return f"Ticket {self.ticket_id} for {self.user.email} - {self.event.title}"

    def generate_qr_code(self):
        qr_data = f"Ticket ID: {self.ticket_id} | Event: {self.event.title} | User: {self.user.email}"
        qr = qrcode.make(qr_data)

        # Save QR Code as image
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        self.qr_code.save(f"qr_{self.ticket_id}.png", ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code:  # Generate QR code only if not already generated
            self.generate_qr_code()
        super().save(*args, **kwargs)
# Create your models here.
