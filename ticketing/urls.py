from django.urls import path
from .views import book_ticket, ticket_detail

urlpatterns = [
    path('book/<int:event_id>/', book_ticket, name='book_ticket'),
    path('detail/<uuid:ticket_id>/', ticket_detail, name='ticket_detail'),
]