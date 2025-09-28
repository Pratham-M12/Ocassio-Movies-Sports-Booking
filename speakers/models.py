from django.db import models
from django.conf import settings
from events.models import Event

class Guest(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    topic = models.CharField(max_length=255)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='guests')

    def __str__(self):
        return f"{self.name} - {self.organization}"

class Speaker(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    bio = models.TextField()
    topic = models.CharField(max_length=255)
    organization = models.CharField(max_length=255, blank=True, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='speakers')

    def __str__(self):
        return f"{self.name} - {self.topic}"