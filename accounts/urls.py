from django.urls import path
from .views import ProfileView, LoginView, HomeView, SignUpView, LogoutView

app_name = 'accounts'

urlpatterns = [
    path('', HomeView, name='home'),
    path('login/', LoginView, name='login'),
    path('profile/', ProfileView, name='profile'),
    path('signup/', SignUpView, name='signup'),
    path('logout/', LogoutView, name='logout'),
]