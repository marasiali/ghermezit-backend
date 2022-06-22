#!/bin/sh
set -e


if [ "$DJANGO_KAFKA_INSTANCE" -eq "1" ]; then
    echo "Waiting for kafka"
    while ! nc -z broker 9092; do
        sleep 0.1
    done

    echo "kafka started"
fi



python manage.py migrate --noinput

python manage.py collectstatic --noinput

exec "$@"
