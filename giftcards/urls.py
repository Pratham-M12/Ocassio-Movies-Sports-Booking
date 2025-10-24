from django.urls import path
from . import views

app_name = 'giftcards'

urlpatterns = [
    path("", views.giftcards_view, name='home')
]