from random import randint
import ghasedakpack
import kavenegar
from django.conf import settings
from abc import ABC, abstractmethod
from mainapp.models import ActivationCode
from mainapp.kafka import get_producer


class SmsManager(ABC):
    default_sender = None
    provider_name = None

    @abstractmethod
    def send(self, message: str, receptor: str, linenumber: str = default_sender) -> bool:
        pass

    def send_activation_code(self, receptor, code, line_number: str = default_sender) -> bool:
        msg = f"کد فعالسازی شما:\n{code}"
        return self.send(msg, receptor, line_number)


class KafkaSenderAdapter(SmsManager):
    provider_name = 'kafka'

    def __init__(self, provider: SmsManager):
        self.provider = provider
        self.kafka_producer = get_producer()

    def send(self, message: str, receptor: str, linenumber: str = None) -> bool:
        if linenumber is None:
            linenumber = self.provider.default_sender
        is_sent = self.kafka_producer.send(settings.KAFKA_SMS_TOPIC, {
            'backend': self.provider.provider_name,
            'message': message,
            'receptor': receptor,
            'linenumber': linenumber,
        })
        if is_sent:
            print(f'Message sent to kafka for sending sms to {receptor} using {self.provider.provider_name}')
        else:
            print(f'Error in sending message to kafka for sending sms to {receptor} using {self.provider.provider_name}')
        return is_sent


class ConsoleSMS(SmsManager):
    default_sender = '10008566'
    provider_name = 'console'

    def send(self, message: str, receptor: str, linenumber: str = default_sender) -> bool:
        print(f'Sending sms in test mode:')
        print(f'Receptor: {receptor}')
        print(f'=============\n{message}\n=============')
        return True


class GhasedakSMSAdapter(SmsManager):
    default_sender = '10008566'
    provider_name = 'ghasedak'

    def __init__(self, provider):
        self.__provider = provider
    
    def send(self, message: str, receptor: str, linenumber: str = default_sender) -> bool:
        return self.__provider.send({'message':message, 'receptor': receptor, 'linenumber': linenumber })
    

class KavenegarSMSAdapter(SmsManager):
    default_sender = '10008663'
    provider_name = 'kavenegar'

    def __init__(self, provider):
        self.__provider = provider

    def send(self, message: str, receptor: str, linenumber: str = default_sender) -> bool:
        return self.__provider.sms_send({'message':message, 'receptor': receptor, 'sender': linenumber })


def get_sms_manager(sms_backend: str = None, kafka_enabled = settings.KAFKA_ENABLED):
    if sms_backend is None:
        sms_backend = settings.SMS_BACKEND
    if sms_backend == 'console':
        sms_manager = ConsoleSMS()
    elif sms_backend == 'ghasedak':
        sms_manager = GhasedakSMSAdapter(ghasedakpack.Ghasedak(settings.GHASEDAK_API_KEY))
    elif sms_backend == 'kavenegar':
        sms_manager = KavenegarSMSAdapter(kavenegar.KavenegarAPI(settings.KAVENEGAR_API_KEY))
    else:
        raise ValueError('Invalid sms backend!')
    if kafka_enabled:
        sms_manager = KafkaSenderAdapter(sms_manager)
    return sms_manager


def generate_activation_code(user) -> int:
    code = str(randint(100000, 999999))
    ActivationCode.objects.create(user=user, code=code)
    print(f'Activation code generated: {code}')
    return code