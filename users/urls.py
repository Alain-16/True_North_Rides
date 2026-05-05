from django.urls import path
from .views import RequestOtpView,verifyOtpView,completeProfileView,IDVerificationView,DriverRegistrationView

urlpatterns =[
    path('request-otp/', RequestOtpView.as_view(), name='request-otp'),
    path('verify-otp/',verifyOtpView.as_view(), name='verify-otp'),
    path('complete-profile/',completeProfileView.as_view(),name='complete-profile'),
    path('verify-id/',IDVerificationView.as_view(),name='verify-id'),
    path('register-driver/',DriverRegistrationView.as_view(),name='register-driver'),

]