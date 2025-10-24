from django.urls import path
from . import views

app_name = "sports"

urlpatterns = [
    path("main/", views.sports_view, name="home"),
    path('<slug:slug>/seat_selection/', views.seat_selection_view, name='seat_selection'),
    path('confirm_booking/', views.confirm_booking, name='confirm_booking'),
    path('<slug:slug>/payment/', views.payment_view, name='payment'),
    path("<slug:slug>/confirmation/", views.sports_confirmation, name="confirmation"),
    path("ticket_template/", views.sports_ticket_template, name="ticket_template"),
]
