from django.contrib import admin
from .models import Speaker, Guest

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'topic', 'event')
    search_fields = ('name', 'email', 'topic')

@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'topic', 'event')
    search_fields = ('name', 'email', 'organization')