from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import RequestOtpSerializer,verifyOtpSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OTPCode, User
from .services import generate_otp, send_otp


class RequestOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = RequestOtpSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_100_CONTINUE)
        phone_number = serializer.validated_data['phone_number']
        email = serializer.validated_data.get('email','')

        user,created = User.objects.get_or_create(phone_number=phone_number,defaults={'email':email,'full_name':''},)

        if not created and email and not user.email:
            user.email = email
            user.save(update_fields=['email'])
        
        OTPCode.objects.filter(user=user,is_used=False).update(is_used=True)
        code = generate_otp()
        OTPCode.objects.create(user=user,code=code)
        send_otp(user,code)

        return Response({'detail':'OTP sent successfully'},status=status.HTTP_200_OK)
    


class verifyOtpView(APIView):
    permission_classes =[AllowAny]

    def post(self,request):
        serializer = verifyOtpSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
        phone_number = serializer.validated_data['phone_number']
        submitted_code = serializer.validated_data['code']

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response({"detail":"User with this phone number does not exist"},status=status.HTTP_404_NOT_FOUND)
        
        otp =(
            OTPCode.objects.filter(user=user,is_used=False).order_by('-created_at').first()
        )

        if otp is None or otp.code != submitted_code:
            return Response(
                {"detail":"invalid phone number or otp"},
                status = status.HTTP_400_BAD_REQUEST,
            )
        if otp.is_expired():
            return Response(
                {"detail":"otp has expired please request a new one"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        otp.is_used = True
        otp.save(update_fields=['is_used'])

        user.is_phone_verified = True
        user.registration_step = User.RegistrationStep.PROFILE
        user.save(update_fields=['is_phone_verified','registration_step'])

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "Access":str(refresh.access_token),
                "refresh":str(refresh),
                "registration_step":user.registration_step,
            },
            status = status.HTTP_200_OK

        )

