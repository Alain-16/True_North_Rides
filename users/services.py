import secrets
from django.conf import settings
from django.core.mail import send_mail

def generate_otp() -> str:
    return f"{secrets.randbelow(1000000):06d}"

def send_otp(user,code:str)-> None:
    backend = getattr(settings,'OTP_BACKEND','email')
    if backend == 'email':
        _send_via_email(user,code)
    elif backend == 'africas_talking':
        _send_via_phone(user,code)
    else:
        raise ValueError(f"Unknown OTP_BACKEND: '{backend}")

def _send_via_email(user,code:str) -> None:
    send_mail(
        subject='Your True North Rides verification code',
        message=(
            f"Hi{user.full_name},\n\n"
            f"your true north rides verification code is: {code} \n\n"
            f"this code will expire in 10 minutes.\n"
            f"if you did not request this code, please ignore this message.\n\n"
            f"Best regards,\n"
            f"True North Rides Team"
        ),
        from_email = settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

def _send_via_phone(user,code:str)-> None:
      # import africastalking                                                                                                                                                          
      # africastalking.initialize(
      #     username=settings.AT_USERNAME,                                                                                                                                             
      #     api_key=settings.AT_API_KEY,
      # )                                                                                                                                                                              
      # sms = africastalking.SMS
      # sms.send(                                                                                                                                                                      
      #     message=f"Your RwandaRide code is {code}. Expires in 10 minutes.",
      #     recipients=[user.phone_number],                                                                                                                                            
      #     sender_id=settings.AT_SENDER_ID,  # e.g. 'RWANDARIDE'
      # ) 
      raise NotImplementedError(
          "Phone OTP sending is not implemented yet. Please set OTP_BACKEND to 'email' or implement the phone sending logic."
      )

