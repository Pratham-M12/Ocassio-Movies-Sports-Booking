from django.contrib import admin
from .models import SportsMatch
@admin.register(SportsMatch)
class SportsMatchAdmin(admin.ModelAdmin):
    list_display = ('title', 'venue', 'date', 'category')
    prepopulated_fields = {"slug": ("title",)}
