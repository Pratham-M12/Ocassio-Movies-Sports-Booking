from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from django.contrib.auth import get_user_model
from .models import CustomUser
from .forms import RegistrationForm
from django.core.mail import send_mail

# Create your views here.

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False #Prevent login before email verification
            user.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return render(request, 'users/home.html')
            else:
                messages.error(request, "Invalid email or password.")
        
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

@login_required

def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')
def home(request):
    return render(request, 'users/home.html')