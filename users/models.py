from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
# Create your models here.


class User(AbstractBaseUser,PermissionsMixin):

    class RegistrationStep(models.TextChoices):
        PHONE_OTP = 'phone_otp', 'Phone OTP Verification'
        PROFILE = 'profile', 'Profile Completion'
        ID_VERiFICATION = 'id_verification', 'ID Verification'
        COMPLETED = 'completed','Completed'

    
    class VerificationStatus(models.TextChoices):
        PENDING ='pending','Pending'
        VERIFIED ='verified', 'Verified'
        REJECTED = 'rejected','rejected'

    phone_number = models.CharField(unique=True,max_lenght=20)
    email = models.EmailField(blank=True)
    full_name = models.CharField(blank=False,max_length=255)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)


    is_phone_verified = models.BooleanField(default=False)
    registration_step = models.CharField(max_length=20,choices=RegistrationStep,default=RegistrationStep.PHONE_OTP)
    verfication_status = models.CharField(max_lenght=20,choices=VerificationStatus,default=VerificationStatus.PENDING)

    national_id_number = models.CharField(max_length=50,blank=True,unique=True)
    id_card_photo = models.ImageField(upload_to='id_cards/',blank=True,null=True)
    selfie_photo = models.ImageField(upload_to='selfies/',blank=True)
    date_of_birth = models.DateField(blank=True)
    rejection_reason = models.TextField(blank=True)

    obejects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"
    