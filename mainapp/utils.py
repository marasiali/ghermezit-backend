from random import randint
import ghasedakpack
import kavenegar
from django.conf import settings
from abc import ABC, abstractmethod
from mainapp.models import ActivationCode


class SmsManager(ABC):
    default_sender = None

    @abstractmethod
    def send(self, message: str, receptor: str, linenumber: str = default_sender) -> bool:
        pass

    def send_activation_code(self, receptor, code, line_number: str = default_sender) -> bool:
        msg = f"کد فعالسازی شما:\n{code}"
        return self.send(msg, receptor, line_number)


class ConsoleSMS(SmsManager):
    default_sender = '10008566'

    def send(self, message: str, receptor: str, linenumber: str = default_sender) -> bool:
        print(f'Sending sms in test mode:')
        print(f'Receptor: {receptor}')
        print(f'=============\n{message}\n=============')
        return True


class GhasedakSMSAdapter(SmsManager):
    default_sender = '10008566'

    def __init__(self, provider):
        self.__provider = provider
    
    def send(self, message: str, receptor: str, linenumber: str = default_sender) -> bool:
        return self.__provider.send({'message':message, 'receptor': receptor, 'linenumber': linenumber })
    

class KavenegarSMSAdapter(SmsManager):
    default_sender = '10008663'

    def __init__(self, provider):
        self.__provider = provider

    def send(self, message: str, receptor: str, linenumber: str = default_sender) -> bool:
        return self.__provider.sms_send({'message':message, 'receptor': receptor, 'sender': linenumber })


def get_sms_manager(sms_backend: str = None):
    if sms_backend is None:
        sms_backend = settings.SMS_BACKEND
    if sms_backend == 'console':
        return ConsoleSMS()
    elif sms_backend == 'ghasedak':
        return GhasedakSMSAdapter(ghasedakpack.Ghasedak(settings.GHASEDAK_API_KEY))
    elif sms_backend == 'kavenegar':
        return KavenegarSMSAdapter(kavenegar.KavenegarAPI(settings.KAVENEGAR_API_KEY))
    raise ValueError('Invalid sms backend!')


def generate_activation_code(user) -> int:
    code = str(randint(100000, 999999))
    ActivationCode.objects.create(user=user, code=code)
    print(f'Activation code generated: {code}')
    return code