from django.conf import settings
from rest_framework import serializers


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