import json
import logging
import pika
import asyncio
from _thread import start_new_thread
from typing import Callable, Iterable, Coroutine, Any, Type
from dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class Queue:
    name: str
    x_dead_letter_exchange: str = None
    x_dead_letter_routing_key: str = None
    message_ttl: int = 0
    durable: bool = False
    exclusive: bool = False
    auto_ack: bool = False

    def validate(self, channel):
        try:
            channel.queue_declare(
                queue=self.name,
                passive=True
            )
            return True
        except:
            return False

    def delete(self, channel, if_empty: bool = False, if_unused: bool = False):
        return channel.queue_delete(
            queue=self.name,
            if_empty=if_empty,
            if_unused=if_unused
        )

    def create(self, channel, raise_exc: bool = False):
        args = {}

        if self.message_ttl:
            args['x-message-ttl'] = self.message_ttl

        if self.x_dead_letter_routing_key:
            args['x-dead-letter-exchange'] = self.x_dead_letter_exchange

        if self.x_dead_letter_routing_key:
            args['x-dead-letter-routing-key'] = self.x_dead_letter_routing_key

        return channel.queue_declare(
            queue=self.name,
            exclusive=self.exclusive,
            auto_delete=self.auto_ack,
            durable=self.durable,
            arguments=args,
            passive=False
        )


@dataclass
class DecoratedFunction:
    queue: Queue
    function: Callable
    message_filters: Iterable[Callable] = None
    input_class: Type[BaseModel] = None

    def validate_message(self, message: Type[BaseModel]):
        if not self.message_filters:
            return True

        return any(
            [
                message_filter(message) for message_filter in self.message_filters
            ]
        )


@dataclass
class Exchange:
    name: str
    exchange_type: str = 'direct'
    durable: bool = False

    def validate(self, channel):
        try:
            channel.exchange_declare(
                exchange=self.name,
                exchange_type=self.exchange_type,
                passive=True
            )
            return True
        except:
            return False

    def delete(self, channel):
        if self.validate(channel):
            channel.exchange_delete(
                exchange=self.name
            )
            return True, self

        return False, None

    def bind(self, channel, queue, routing_key: str):
        if self.validate(channel):
            channel.queue_bind(
                queue=queue.name,
                routing_key=routing_key,
                exchange=self.name
            )
            return self, queue, routing_key

        raise ValueError(
            'Обменник не найден!'
        )

    def create(self, channel):
        channel.exchange_declare(
            exchange=self.name,
            exchange_type=self.exchange_type,
            durable=self.durable,
            passive=False
        )
        return True, self

    async def send_message(self, channel, routing_key: str, message: dict, properties: pika.BasicProperties = None):
        try:
            message_json = json.dumps(message)
        except json.JSONDecodeError:
            raise ValueError(
                'Указанное сообщение не является JSON-сериализуемым объектом.'
            )

        return channel.basic_publish(
            exchange=self.name,
            routing_key=routing_key,
            body=message_json,
            properties=properties
        )


@dataclass
class Binding:
    exchange: Exchange
    queue: Queue
    routing_key: str

    def make(self, channel):
        self.exchange.bind(
            channel=channel,
            queue=self.queue,
            routing_key=self.routing_key
        )


@dataclass
class Message:
    decorated_function: DecoratedFunction
    payload: str | bytes
    properties: pika.BasicProperties
    channel: pika.adapters.blocking_connection.BlockingChannel
    method: pika.spec.Basic.Deliver
    input_class: Type[BaseModel] = None

    async def get_data(self):
        json_data = self.json_data()

        if not json_data:
            logging.error('Получено сообщение некорректного формата (не JSON).')
            await self.nack(requeue=False)
            return None

        return json_data

    def json_data(self):
        try:
            if self.input_class:
                return self.input_class.model_validate_json(
                    json_data=self.payload
                )

            return BaseModel.model_validate_json(self.payload)
        except ValueError:
            return {}

    async def nack(self, requeue: bool = False):
        return self.channel.basic_nack(
            delivery_tag=self.delivery_tag,
            requeue=requeue
        )

    async def ack(self):
        return self.channel.basic_ack(
            delivery_tag=self.delivery_tag
        )

    async def reject(self, requeue: bool = False):
        return self.channel.basic_reject(
            delivery_tag=self.delivery_tag,
            requeue=requeue
        )

    @property
    def is_redelivered(self):
        return self.method.redelivered

    @property
    def routing_key(self):
        return self.method.routing_key

    @property
    def delivery_tag(self):
        return self.method.delivery_tag

    @property
    def exchange(self):
        return self.method.exchange

    def _validate_message(self):
        return self.decorated_function.validate_message(
            self.json_data()
        )


class BrokerManager:
    def __init__(self):
        self.__decorated_functions: list[DecoratedFunction] = []
        self.__channel = None
        self.__connection = None
        self.default_exchange = 'chains'
        self.__loop = asyncio.get_event_loop()

        self.__queues = []
        self.__exchanges = []
        self.__bindings = []

    def set_loop(self, loop: asyncio.BaseEventLoop):
        self.__loop = loop

    @property
    def loop(self):
        return self.__loop

    def __get_bindings_for_queue(self, queue: Queue):
        if queue not in self.__queues:
            raise ValueError(
                'Данная очередь не зарегистрирована в менеджер-классе.'
            )

        return list(filter(lambda binding: binding.queue == queue, self.__bindings))

    def __get_bindings_for_exchange(self, exchange: Exchange):
        if exchange not in self.__exchanges:
            raise ValueError(
                'Данный обменник не зарегистрирован в менеджер-классе.'
            )

        return list(filter(lambda binding: binding.exchange == exchange, self.__bindings))

    def __get_binding_by_routing_key(self, routing_key: str):
        if not routing_key:
            raise ValueError(
                'Routing key не указан.'
            )

        results = list(filter(lambda binding: binding.routing_key == routing_key, self.__bindings))
        if results:
            return results[-1]
        return None

    def consume(self, queue_name: str, input_class: Type[BaseModel] = None, filters: list[Callable] = None):
        def wrapper(func):
            if not asyncio.iscoroutinefunction(func):
                raise TypeError(
                    f'Функция {func} должна быть coroutine.'
                )

            queue = self.__get_queue_by_name(queue_name)
            if not queue:
                raise ValueError(
                    'Данная очередь не зарегистрирована в менеджере.'
                )

            self.__decorated_functions.append(
                DecoratedFunction(
                    queue=queue,
                    function=func,
                    message_filters=filters,
                    input_class=input_class
                )
            )

        return wrapper

    def __get_queue_by_name(self, queue_name: str):
        results = list(filter(lambda queue: queue.name == queue_name, self.__queues))
        if results:
            return results[-1]
        return None

    def __get_exchange_by_name(self, exchange_name: str):
        results = list(filter(lambda exchange: exchange.name == exchange_name, self.__exchanges))
        if results:
            return results[-1]
        return None

    def __default_callback(self, channel, method, properties, body):
        routing_key = method.routing_key

        binding = self.__get_binding_by_routing_key(routing_key=routing_key)
        if not binding:
            return

        queue = binding.queue
        exchange = binding.exchange

        decorated_functions = list(
            filter(
                lambda function:
                    function.queue == queue,
                self.__decorated_functions
            )
        )

        if not decorated_functions:
            return

        for decorated_function in decorated_functions:
            message_instance = Message(
                payload=body,
                properties=properties,
                channel=channel,
                method=method,
                decorated_function=decorated_function,
                input_class=decorated_function.input_class
            )

            if not message_instance._validate_message() or not message_instance.json_data():
                del message_instance
                continue

            if decorated_function.queue.auto_ack:
                self.channel.basic_ack(delivery_tag=message_instance.delivery_tag, multiple=False)

            return asyncio.run_coroutine_threadsafe(
                coro=decorated_function.function(message_instance, exchange=exchange),
                loop=self.__loop
            )

    async def send_message(self, routing_key: str, message: str, properties: dict = None):
        if properties:
            properties = pika.BasicProperties(**properties)
        else:
            properties = None

        return self.channel.basic_publish(
            exchange=self.default_exchange,
            routing_key=routing_key,
            body=message.encode(),
            properties=properties
        )

    def create_connection(self, auth_url: str):
        connection_params = pika.URLParameters(auth_url)

        connection = pika.BlockingConnection(
            connection_params
        )

        self.connection = connection
        return connection

    def create_queue(self,
                     queue_name: str,
                     auto_ack: bool = False,
                     durable: bool = False,
                     binding: Binding = None,
                     **arguments
                     ):
        channel = self.channel

        channel.queue_declare(
            queue=queue_name,
            auto_delete=auto_ack,
            durable=durable,
            arguments=arguments
        )

        if binding:
            channel.queue_bind(
                queue=queue_name,
                exchange=binding.exchange.name,
                routing_key=binding.routing_key
            )

        return queue_name

    @property
    def channel(self) -> pika.adapters.blocking_connection.BlockingChannel:
        if not self.__channel:
            self.__channel = self.connection.channel()
            self.__channel.flow(active=True)

        return self.__channel

    @property
    def connection(self) -> pika.adapters.BlockingConnection:
        if not self.__connection:
            raise ConnectionError(
                'Подключение к брокеру не осуществлено.'
            )

        return self.__connection

    @connection.setter
    def connection(self, value: pika.BlockingConnection):
        self.__connection = value

    @property
    def queues(self):
        return self.__queues.copy()

    @queues.setter
    def queues(self, value: list[Queue]):
        self.__queues.clear()
        self.__queues = value

    @property
    def exchanges(self):
        return self.__exchanges.copy()

    @exchanges.setter
    def exchanges(self, value: list[Exchange]):
        self.__exchanges.clear()
        self.__exchanges = value

    def __on_open_callback(self, **_):
        for exchange in self.exchanges:
            exchange.create(channel=self.channel)

        for queue in self.queues:
            queue.create(self.channel)

        for binding in self.bindings:
            binding.make(channel=self.channel)

        print('[!] Polling запущен!')

    @property
    def bindings(self):
        return self.__bindings.copy()

    @bindings.setter
    def bindings(self, value: list[Binding]):
        self.__bindings.clear()
        self.__bindings = value

    def start(self):
        if not self.__decorated_functions:
            raise NotImplemented(
                'Callback-функции не указаны.'
            )

        self.__on_open_callback()

        for callback in self.__decorated_functions:
            self.channel.basic_consume(
                queue=callback.queue.name,
                exclusive=callback.queue.exclusive,
                auto_ack=False,
                on_message_callback=self.__default_callback
            )

        start_new_thread(self.__loop.run_forever, ())
        self.channel.start_consuming()

