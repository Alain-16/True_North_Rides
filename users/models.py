from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
# Create your models here.


class User(AbstractBaseUser,PermissionsMixin):
    phone_number = models.CharField(unique=True,max_lenght=20)
    email = models.EmailField(blank=True)
    full_name = models.CharField(blank=False,max_length=255)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    obejects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"
    