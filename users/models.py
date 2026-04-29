from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
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
    
    class Gender(models.TextChoices):
        MALE = 'male','Male'
        FEMALE ='female','Female'

    phone_number = models.CharField(unique=True,max_length=20)
    email = models.EmailField(blank=True)
    full_name = models.CharField(blank=False,max_length=255)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)


    is_phone_verified = models.BooleanField(default=False)
    registration_step = models.CharField(max_length=20,choices=RegistrationStep.choices,default=RegistrationStep.PHONE_OTP)
    verfication_status = models.CharField(max_length=20,choices=VerificationStatus.choices,default=VerificationStatus.PENDING)

    national_id_number = models.CharField(max_length=50,blank=True,unique=True)
    id_card_photo = models.ImageField(upload_to='id_cards/',blank=True,null=True)
    selfie_photo = models.ImageField(upload_to='selfies/',blank=True)
    date_of_birth = models.DateField(blank=True)
    rejection_reason = models.TextField(blank=True)

    gender = models.CharField(max_length=20, choices=Gender.choices,blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/',blank=True)

    emergency_contact_name = models.CharField(max_length=255,blank=True)
    emergency_contact_phone = models.CharField(max_length=20,blank=True)

    is_driver = models.BooleanField(default=False)

    driver_verification_status = models.CharField(max_length=20,choices=VerificationStatus.choices,default=VerificationStatus.PENDING,blank=True,null=True)
    
    total_rides_as_driver = models.PositiveIntegerField(default=0)
    total_rides_as_passenger = models.PositiveIntegerField(default=0)

    trust_score = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)

    obejects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"

class OTPCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='otp_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = 'otp_codes'
    
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)


    def __str__(self):
        return f"OTP for {self.user.phone_number} - Code: {self.code}"