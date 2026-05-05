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
        PREFER_NOT_TO_SAY = 'prefer_not_to_say','Prefer not to say'
    
    class FuelType(models.TextChoices):
        PETROL = 'petrol','petrol'
        DIESEL = 'diesel','diesel'
        ELECTRIC = 'electric','electric'
    class EfficiencySource(models.TextChoices):                                                                                                                                      
        FUELECONOMY_API = 'fueleconomy_api', 'FuelEconomy API'
        ENGINE_SIZE_FALLBACK = 'engine_size_fallback', 'Engine Size Fallback'                                                                                                        
        MANUAL_ENTRY = 'manual_entry', 'Manual Entry'


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

    driver_license_number = models.CharField(max_length=50,blank=True, unique=True)
    driver_license_expiry_date = models.DateField(null=True,blank=True)
    driver_license_photo = models.ImageField(upload_to='driver_licenses/',blank=True,null=True)

    vehicle_make = models.CharField(max_length=20,blank=True)
    vehicle_model = models.CharField(max_length=20,blank=True)
    vehicle_year = models.PositiveIntegerField(null=True,blank=True)
    vehicle_fuel_type = models.CharField(max_length=20,blank=True,choices=FuelType.choices)
    vehicle_engine_cc = models.PositiveIntegerField(null=True, blank=True)                                                                                                           
    vehicle_color = models.CharField(max_length=50, blank=True)
    vehicle_plate = models.CharField(max_length=20, blank=True)
    vehicle_registration_photo = models.ImageField(
          upload_to='vehicle_registrations/', blank=True, null=True
      )                                                                                                                                                                                
    vehicle_photo = models.ImageField(
          upload_to='vehicle_photos/', blank=True, null=True                                                                                                                           
      )

    vehicle_system_efficiency_km_l = models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True)
    vehicle_driver_adjusted_efficiency_km_l = models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True)
    vehicle_effective_efficiency_km_l = models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True)
    vehicle_efficiency_source = models.CharField(max_length=20,choices=EfficiencySource.choices,blank=True,null=True)   


    objects = UserManager()

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
    
class VehicleEfficiencyCache(models.Model):
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    fuel_type = models.CharField(max_length=20,choices=User.FuelType.choices)
    api_mpg_combined = models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    base_efficiency_km_l = models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    adjusted_efficiency_km_l = models.DecimalField(max_digits=5,decimal_places=2,null=True,blank=True)
    data_source = models.CharField(max_length=20,choices=User.EfficiencySource.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table ='vehicle_efficiency_cache'
        unique_together =('make','model','year','fuel_type')
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    