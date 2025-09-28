from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegistrationForm(UserCreationForm):
    email=forms.EmailField(required=True)
    first_name=forms.CharField(max_length=100)
    last_name=forms.CharField(max_length=100)

    class Meta:
        model=CustomUser
        fields=['username','email','password1','password2','first_name','last_name']

class LoginForm(forms.Form):
    email=forms.EmailField()
    password=forms.CharField(widget=forms.PasswordInput)