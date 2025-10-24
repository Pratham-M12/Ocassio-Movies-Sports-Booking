from django.urls import path
from . import api_views

app_name = 'movies_api'

urlpatterns = [
    # Movie API endpoints
    path('movies/', api_views.MovieListAPIView.as_view(), name='movie_list'),
    path('movies/<int:pk>/', api_views.MovieDetailAPIView.as_view(), name='movie_detail'),
    
    # Screening API endpoints
    path('screenings/', api_views.ScreeningListAPIView.as_view(), name='screening_list'),
    path('screenings/<int:pk>/', api_views.ScreeningDetailAPIView.as_view(), name='screening_detail'),
    
    # Ticket API endpoints
    path('tickets/', api_views.TicketListCreateAPIView.as_view(), name='ticket_list_create'),
    path('tickets/<int:pk>/', api_views.TicketDetailAPIView.as_view(), name='ticket_detail'),
    
    # Theater API endpoints
    path('theaters/', api_views.TheaterListAPIView.as_view(), name='theater_list'),
    path('theaters/<int:pk>/', api_views.TheaterDetailAPIView.as_view(), name='theater_detail'),
    
    # Genre API endpoints
    path('genres/', api_views.GenreListAPIView.as_view(), name='genre_list'),
]
