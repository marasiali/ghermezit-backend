import ghasedakpack
from django.conf import settings

sms = ghasedakpack.Ghasedak(settings.GHASEDAK_API_KEY)

def send_sms(message, receptor):
    sms.send({'message':message, 'receptor' : receptor, 'linenumber': '10008566' })

def send_activation_code_sms(phone_number, code):
    msg = f"کد فعالسازی شما:\n{code}"
    send_sms(msg, phone_number)
