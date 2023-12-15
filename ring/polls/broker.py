import pika
from django.conf import settings


params = pika.URLParameters(settings.BROKER_URL)
connection = pika.BlockingConnection(
    params
)

