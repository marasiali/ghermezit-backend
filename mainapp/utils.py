from random import randint
import ghasedakpack
from django.conf import settings

from mainapp.models import ActivationCode

if settings.SMS_ENABLED:
    sms = ghasedakpack.Ghasedak(settings.GHASEDAK_API_KEY)

def send_sms(message, receptor):
    if settings.SMS_ENABLED:
        sms.send({'message':message, 'receptor' : receptor, 'linenumber': '10008566' })
    else:
        print(f'Sending sms in test mode:')
        print(f'Receptor: {receptor}')
        print(f'=============\n{message}\n=============')


def send_activation_code_sms(phone_number, code):
    msg = f"کد فعالسازی شما:\n{code}"
    send_sms(msg, phone_number)

def generate_and_send_activation_code(user) -> int:
    code = str(randint(100000, 999999))
    ActivationCode.objects.create(user=user, code=code)
    print(f'Activation code generated: {code})')
    send_activation_code_sms(user.phone_number, code)
    return code