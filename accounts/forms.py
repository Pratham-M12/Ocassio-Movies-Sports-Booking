from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()

class SignUpForm(UserCreationForm):
    fullname = forms.CharField(max_length=100,required=True,widget=forms.TextInput(attrs={'placeholder': 'Full Name','class': 'input-field'}))
    email = forms.EmailField(required=True,widget=forms.EmailInput(attrs={'placeholder': 'Email Address','class': 'input-field'}))
    class Meta:
        model = User
        fields = ['fullname', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'input-field')
        self.fields['username'].widget.attrs.update({'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data.get('fullname', '').strip()
        first_name, *last_name = full_name.split(' ', 1)
        user.first_name = first_name
        user.last_name = last_name[0] if last_name else ''
        user.email = self.cleaned_data['email']
        user.fullname = full_name
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    identifier = forms.CharField(
        label="Email or Username",
        widget=forms.TextInput(attrs={
            'placeholder': 'Email or Username',
            'class': 'input-field'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'input-field'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get('identifier')
        password = cleaned_data.get('password')

        if identifier and password:
            user = authenticate(username=identifier, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email/username or password")
            self.user = user
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)
