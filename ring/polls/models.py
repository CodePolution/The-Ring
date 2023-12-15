import uuid
import json
from django.db import models


class ChainStatus(models.Model):
    title = models.CharField(null='true', max_length=50)
    status = models.BooleanField(default=False)


class Submit(models.Model):
    one = models.IntegerField(null='true')
    two = models.IntegerField(null='true')
    three = models.IntegerField(null='true')
    four = models.IntegerField(null='true')


class Task(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
    )

    request_data = models.TextField(
        null=False,
        blank=False,
        verbose_name='Тело запроса',
    )

    response_data = models.TextField(
        null=True,
        blank=True,
        verbose_name='Тело ответа'
    )

    C = type('C', (object,), {})

    @property
    def is_done(self):
        return bool(self.response_data)

    @property
    def request_data_dump(self):
        if self.request_data:
            return json.loads(self.request_data)

        return None

    @property
    def response_data_dump(self):
        if self.response_data:
            return json.loads(self.response_data)

        return None

    @property
    def response_fields(self):
        if not self.is_done:
            return {}

        data = self.response_data_dump
        return data['fields']

