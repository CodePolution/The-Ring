import pika
from .models import Task
import json
from django.conf import settings
from threading import Thread


params = pika.URLParameters(settings.BROKER_URL)
connection = pika.BlockingConnection(
    params
)

channel = connection.channel()


def create_task(fields: list[dict]):
    send_data = {'fields': fields}
    send_data_json = json.dumps(send_data)

    task = Task.objects.create(
        request_data=send_data_json,
        response_data=None
    )

    send_data['uuid'] = str(task.uuid)
    send_data = json.dumps(send_data)

    channel.basic_publish(
        exchange=settings.BROKER_EXCHANGE,
        routing_key='chain1',
        body=send_data.encode(),
    )

    return task


class Consumer(Thread):

    @staticmethod
    def process_message(thread_channel, method, properties, body):
        print(body)

        body = body.decode()
        if not body:
            return

        body_json = json.loads(body)

        task_uuid = body_json['uuid']
        task_instance = Task.objects.filter(uuid=task_uuid)
        if not task_instance.exists():
            return

        task_instance = task_instance.first()
        task_instance.response_data = body
        task_instance.save()

    def run(self):
        new_channel = connection.channel(channel_number=228)
        new_channel.basic_consume(
            queue=settings.BROKER_LAST_QUEUE,
            on_message_callback=self.process_message,
            auto_ack=True,
            exclusive=False
        )
        return channel.start_consuming()
