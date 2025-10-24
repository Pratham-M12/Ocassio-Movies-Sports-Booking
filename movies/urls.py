from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path("main/", views.movies_view, name='home'),
    # Movie showtime URLs
    path("<slug:movie_slug>/showtimes/", views.showtimes, name="showtimes"),
    path("<slug:movie_slug>/showtimes/<int:showtime_id>/", views.seat_selection, name="seat_selection"),
    path("<slug:movie_slug>/payment/", views.payment, name="payment"),
    path("<slug:movie_slug>/confirmation/", views.confirmation, name="confirmation"),
    path("ticket_template/", views.ticket_template, name='ticket_template'),
    # Save Ticket URLs
    path('api/save_ticket/', views.save_ticket, name='save_ticket'),
    # Showtime URLs
    path('showtime/<int:showtime_id>/seats/', views.get_seats, name='get_seats'),
    path('confirm-booking/', views.confirm_booking, name='confirm_booking')
]