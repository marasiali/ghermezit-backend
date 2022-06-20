from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from mainapp.kafka import get_consumer
from mainapp.utils import get_sms_manager

class Command(BaseCommand):
    help = 'Run kafka consumer'

    def handle(self, *args, **options):
        consumer = get_consumer(settings.KAFKA_SMS_TOPIC)
        self.stdout.write('Wait for new message...')
        for msg in consumer:
            print('Recieved new message:', msg.value)
            is_sent = get_sms_manager(msg.value['backend'], False).send(
                message=msg.value['message'],
                receptor=msg.value['receptor'],
                linenumber=msg.value['linenumber']
            )
            if is_sent:
                print(f"sms sent to {msg.value['receptor']} using {msg.value['backend']}")
            else:
                print(f"Error in sending sms to {msg.value['receptor']} using {msg.value['backend']}")
