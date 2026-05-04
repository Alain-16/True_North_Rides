from django.conf import settings
from rest_framework import serializers
from django.utils import timezone
from .models import User


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
