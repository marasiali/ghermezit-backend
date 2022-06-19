import json
from kafka import KafkaProducer, KafkaConsumer


_kafka_producer = None
_kafka_consumer = None


def get_producer(*args, **kwargs):
    global _kafka_producer
    if _kafka_producer is None:
        _kafka_producer = KafkaProducer(
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            *args,
            **kwargs
        )
    return _kafka_producer

def get_consumer(*args, **kwargs):
    global _kafka_consumer
    if _kafka_consumer is None:
        _kafka_consumer = KafkaConsumer(
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            *args,
            **kwargs
        )
    return _kafka_consumer


