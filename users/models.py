from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] #Keep username for Django admin

    def __str__(self):
        return self.email