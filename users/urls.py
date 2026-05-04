from django.urls import path
from .views import RequestOtpView,verifyOtpView,completeProfileView

urlpatterns =[
    path('request-otp/', RequestOtpView.as_view(), name='request-otp'),
    path('verify-otp/',verifyOtpView.as_view(), name='verify-otp'),
    path('complete-profile/',completeProfileView.as_view(),name='complete-profile')
]