from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, LoginForm

def HomeView(request):
    return render(request, 'accounts/home.html')

def SignUpView(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('accounts:login')
        print(form.errors)
        messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()
    return render(request, 'accounts/login.html', {'signup_form': form, 'login_form': LoginForm()})

def LoginView(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                auth_login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('accounts:home')
            else:
                messages.error(request, "Invalid credentials. Please try again.")
        else:
            messages.error(request, "Invalid Email/Username or Password. Please try again.")
    return render(request,'accounts/login.html',{'login_form': LoginForm(), 'signup_form': SignUpForm()})

@login_required
def LogoutView(request):
    logout(request)
    messages.success(request, "You've been logged out successfully.")
    return redirect('accounts:login')

@login_required
def ProfileView(request):
    user = request.user
    if request.method == "POST":
        user.first_name = request.POST.get("first_name", "")
        user.last_name = request.POST.get("last_name", "")
        user.email = request.POST.get("email", "")
        user.phone_number = request.POST.get("mobile", "")
        user.birthday = request.POST.get("birthday") or None
        user.address_line1 = request.POST.get("addr1", "")
        user.address_line2 = request.POST.get("addr2", "")
        user.landmark = request.POST.get("landmark", "")
        user.pincode = request.POST.get("pincode", "")
        user.city = request.POST.get("city", "")
        user.state = request.POST.get("state", "")
        user.address_type = request.POST.get("save_as", "home")

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("accounts:profile")

    return render(request, "accounts/profile.html", {"user": user})
