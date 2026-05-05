import secrets
from django.conf import settings
from django.core.mail import send_mail
import requests
from .models import User,VehicleEfficiencyCache
from decimal import Decimal,ROUND_HALF_UP
from django.utils import timezone
from datetime import timedelta


FUELECONOMY_BASE_URL ='https://www.fueleconomy.gov/ws/rest/vehicle/'
TERRAIN_CORRECTION_FACTORS = Decimal('0.85')
MPG_TO_KML_FACTOR = Decimal('0.425144')
CACHE_TTL_DAYS = 365

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


def lookup_vehicle_efficiency(make:str,model:str,year:int,fuel_type:str,engine_cc:int | None = None) -> dict:
    cached = VehicleEfficiencyCache.objects.filter(
        make__iexact=make,
        model__iexact=model,
        year=year,
        fuel_type=fuel_type,
    ).first()
    
    if cached and not cached.is_expired():
        return{
            'base_efficiency_km_l': cached.base_efficiency_km_l,
            'adjusted_efficiency_km_l': cached.adjusted_efficiency_km_l,
            'efficiency_source': cached.data_source,
            'api_mpg': cached.api_mpg,
        }
    
    api_result = _fetch_from_api(make,model,year)

    if api_result:
        mpg = Decimal(str(api_result['mpg']))
        base_km_l = (mpg * MPG_TO_KML_FACTOR).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
        adjusted_km_l = (base_km_l * TERRAIN_CORRECTION_FACTORS).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        source = User.EfficiencySource.FUELECONOMY_API
        VehicleEfficiencyCache.objects.update_or_create(
            make=make,
            model=model,
            year=year,
            fuel_type=fuel_type,
            defaults={
                'api_mpg_combined': mpg,
                'base_efficiency_km_l': base_km_l,
                'adjusted_efficiency_km_l': adjusted_km_l,
                'data_source': source,
                'expires_at': timezone.now() + timedelta(days=CACHE_TTL_DAYS),
            }
        )
        return{
            'base_efficiency_km_l': base_km_l,
            'adjusted_efficiency_km_l': adjusted_km_l,
            'efficiency_source': source,
            'api_mpg': mpg,
        }
    return __fallback_from_engine_size(engine_cc)
   

def _fetch_from_api(make:str,model:str,year:int) -> dict | None:
    try:
        options_rep = requests.get(f"{FUELECONOMY_BASE_URL}menu/options?year={year}&make={make}&model={model}",timeout=5)
        options_rep.raise_for_status()
        menu_item = options_rep.json().get('menuItem')

        if not menu_item:
            return None
        
        if isinstance(menu_item,dict):
            menu_item = [menu_item]
            vehicle_id = menu_item[0]['value']
            vehicle_rep = requests.get(f'{FUELECONOMY_BASE_URL}/{vehicle_id}',timeout=5,headers={'Accept':'application/json'})
            vehicle_rep.raise_for_status()
            mpg = vehicle_rep.json().get('comb08',0)

            if not mpg:
                return None
            return{'mpg':mpg}
    except requests.RequestException:
        return None



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




def __fallback_from_engine_size(engine_cc:int | None):
    if engine_cc is None or (1500 <= engine_cc < 2000):
        base_km_l = Decimal('13.0')
    elif engine_cc < 1500:
        base_km_l = Decimal('15.0')
    elif engine_cc < 2500:
        base_km_l = Decimal('10.5')
    else:
        base_km_l = Decimal('8.0')
    
    adjusted_km_l = (base_km_l * TERRAIN_CORRECTION_FACTORS).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return{
        'base_efficiency_km_l': base_km_l,
        'adjusted_efficiency_km_l': adjusted_km_l,
        'efficiency_source': User.EfficiencySource.ENGINE_SIZE_FALLBACK,
        'api_mpg': None,
    }

