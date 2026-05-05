from django.conf import settings
from rest_framework import serializers
from django.utils import timezone
from .models import User
from .services import lookup_vehicle_efficiency
from decimal import Decimal


class RequestOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    email = serializers.EmailField(required=False)

    def validate_phone_number(self,value):
        if not value.startswith('+'):
            raise serializers.ValidationError("Phone number must include country code, e.g. +250788123456")
        if not value[1:].isdigit():
            raise serializers.ValidationError("Phone number must contain only digits after the country code")
        return value
    
    def validate_email(self,data):
        if getattr(settings,'OTP_BACKEND','email') == 'email':
            if not data.get('email'):
                raise serializers.ValidationError("Email is required when OTP_BACKEND is set to 'email'")
        return data


class verifyOtpSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)

class UserProfileSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField(required=False,allow_blank=True)
    date_of_birth = serializers.DateField(required=True)
    emergency_contact_name = serializers.CharField(max_length=255,required=True)
    emergency_contact_phone = serializers.CharField(max_length=20,required=True)

    def validate_emergency_contact_phone(self,value):
        if not value.startswith('+'):
            raise serializers.ValidationError("Emergency contact phone number must include country code, e.g. +250788123456")
        if not value[1:].isdigit():
            raise serializers.ValidationError("Emergency contact phone number must contain only digits after the country code")
        return value
    
    def validate_date_of_birth(self,value):
        today = timezone.now().date()
        
        if value >= today:
            raise serializers.ValidationError("Date of birth cannot be in the future")
        age =(today - value).days
        if age < 18:
            raise serializers.ValidationError("User must be at least 18 years old")
        return value
    
    def save(self,user):
        data = self.validated_data
        user.full_name = data['full_name']
        user.email = data.get('email',user.email)
        user.date_of_birth = data['date_of_birth']
        user.gender = data['gender']
        user.emergency_contact_name = data['emergency_contact_name']
        user.emergency_contact_phone = data['emergency_contact_phone']
        user.registration_step = User.RegistrationStep.ID_VERiFICATION
        user.save(update_fields=['full_name','email','date_of_birth','gender','emergency_contact_name','emergency_contact_phone','registration_step'])


class IDVerificationSerializer(serializers.Serializer):
    national_id_number = serializers.CharField(max_length=16)
    national_id_photo = serializers.ImageField()
    selfie_photo = serializers.ImageField()

    def validate_national_id_number(self,value):
        value = value.strip()
        if len(value) != 16 or not value.isdigit():
            raise serializers.ValidationError("National ID number must be exactly 16 characters long")
        if User.objects.filter(national_id_number=value).exists():
            raise serializers.ValidationError("This national ID number is already in use")
        return value
    
    def save(self,user):
        data = self.validated_data
        user.national_id_number = data['national_id_number']
        user.id_card_photo = data['id_card_photo']
        user.selfie_photo = data['selfie_photo']
        user.verification_status = User.VerificationStatus.PENDING
        user.registration_step = User.RegistrationStep.COMPLETED
        user.save(update_fields=[
            'national_id_number','id_card_photo','selfie_photo','verification_status','registration_step'
        ])


class DriverRegistrationSerializer(serializers.Serializer):
                                                                                                                                                                              
      driver_license_number = serializers.CharField(max_length=50)
      driver_license_expiry = serializers.DateField()
      driver_license_photo = serializers.ImageField()
      vehicle_make = serializers.CharField(max_length=100)                                                                                                                             
      vehicle_model = serializers.CharField(max_length=100)
      vehicle_year = serializers.IntegerField()
      vehicle_fuel_type = serializers.ChoiceField(choices=User.FuelType.choices)                                                                                                       
      vehicle_engine_cc = serializers.IntegerField(required=False, allow_null=True)
      vehicle_color = serializers.CharField(max_length=50)                                                                                                                             
      vehicle_plate = serializers.CharField(max_length=20)
      vehicle_registration_photo = serializers.ImageField()                                                                                                                            
      vehicle_photo = serializers.ImageField()

      driver_efficiency_adjustment = serializers.DecimalField(
          max_digits=5, decimal_places=2, required=False, allow_null=True                                                                                                              
      )
                                                                                                                                                                                       
      def validate_driver_license_expiry(self, value):
          if value <= timezone.now().date():
              raise serializers.ValidationError(                                                                                                                                       
                  "Driving license is expired. Please renew and try again."
              )                                                                                                                                                                        
          return value

      def validate_vehicle_year(self, value):                                                                                                                                          
          current_year = timezone.now().year
          if value < 1980 or value > current_year + 1:                                                                                                                                 
              raise serializers.ValidationError(
                  f"Vehicle year must be between 1980 and {current_year + 1}."
              )                                                                                                                                                                        
          return value
                                                                                                                                                                                       
      def validate(self, data):
          efficiency_result = lookup_vehicle_efficiency(
              make=data['vehicle_make'],
              model=data['vehicle_model'],
              year=data['vehicle_year'],
              fuel_type=data['vehicle_fuel_type'],
              engine_cc=data.get('vehicle_engine_cc'),
          )                                                                                                                                                                            
          self._efficiency_result = efficiency_result
                                                                                                                                                                                       
          adjustment = data.get('driver_efficiency_adjustment')
          if adjustment is not None:
              system_value = efficiency_result['system_efficiency_km_l']                                                                                                               
              diff = abs(Decimal(str(adjustment)) - Decimal(str(system_value)))
              if diff > Decimal('2.0'):                                                                                                                                                
                  raise serializers.ValidationError({
                      'driver_efficiency_adjustment': (                                                                                                                                
                          f"Adjustment must be within ±2 km/L of the system value "                                                                                                    
                          f"({system_value} km/L). You submitted {adjustment} km/L."
                      )                                                                                                                                                                
                  })
                                                                                                                                                                                       
          return data

      def save(self, user):
          data = self.validated_data
          result = self._efficiency_result
          adjustment = data.get('driver_efficiency_adjustment')                                                                                                                                                                                                                                                                                    
          user.driver_license_number = data['driver_license_number']
          user.driver_license_expiry_date = data['driver_license_expiry_date']
          user.driver_license_photo = data['driver_license_photo']

          # Vehicle details                                                                                                                                                            
          user.vehicle_make = data['vehicle_make']
          user.vehicle_model = data['vehicle_model']                                                                                                                                   
          user.vehicle_year = data['vehicle_year']
          user.vehicle_fuel_type = data['vehicle_fuel_type']
          user.vehicle_engine_cc = data.get('vehicle_engine_cc')                                                                                                                       
          user.vehicle_color = data['vehicle_color']
          user.vehicle_plate = data['vehicle_plate']                                                                                                                                   
          user.vehicle_registration_photo = data['vehicle_registration_photo']                                                                                                         
          user.vehicle_photo = data['vehicle_photo']
                                                                                                                                                                                       
          # Efficiency
          user.vehicle_system_efficiency_km_l = result['system_efficiency_km_l']
          user.vehicle_efficiency_source = result['source']                                                                                                                            
  
          if adjustment is not None:                                                                                                                                                   
              user.vehicle_driver_adjusted_efficiency_km_l = adjustment
              user.vehicle_effective_efficiency_km_l = adjustment                                                                                                                      
          else:
              user.vehicle_driver_adjusted_efficiency_km_l = None                                                                                                                      
              user.vehicle_effective_efficiency_km_l = result['system_efficiency_km_l']                                                                                                
  
          user.driver_verification_status = User.VerificationStatus.PENDING                                                                                                            
                  
          user.save(update_fields=[
              'driver_license_number', 'driver_license_expiry', 'driver_license_photo',
              'vehicle_make', 'vehicle_model', 'vehicle_year', 'vehicle_fuel_type',
              'vehicle_engine_cc', 'vehicle_color', 'vehicle_plate',                                                                                                                   
              'vehicle_registration_photo', 'vehicle_photo',
              'vehicle_system_efficiency_km_l', 'vehicle_efficiency_source',                                                                                                           
              'vehicle_driver_adjusted_efficiency_km_l', 'vehicle_effective_efficiency_km_l',                                                                                          
              'driver_verification_status',
          ])                       