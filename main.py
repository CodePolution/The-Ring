import models
import settings
from brokers import BrokerManager, Message, Queue, Exchange, Binding
from logger import Logger

manager = BrokerManager()
logger = Logger()

manager.create_connection('amqp://guest:guest@localhost:5672/')

manager.queues = [
    chain5 := Queue(
        name='chain5',
        auto_ack=False,
        exclusive=False
    ),
    chain4 := Queue(
        name='chain4',
        x_dead_letter_exchange='chains',
        x_dead_letter_routing_key='chain5',
        message_ttl=2000,
        auto_ack=False,
        exclusive=False
    ),
    chain3 := Queue(
        name='chain3',
        x_dead_letter_exchange='chains',
        x_dead_letter_routing_key='chain4',
        message_ttl=2000,
        auto_ack=False,
        exclusive=False
    ),
    chain2 := Queue(
        name='chain2',
        x_dead_letter_exchange='chains',
        x_dead_letter_routing_key='chain3',
        message_ttl=2000,
        auto_ack=False,
        exclusive=False
    ),
    chain1 := Queue(
        name='chain1',
        x_dead_letter_exchange='chains',
        x_dead_letter_routing_key='chain2',
        message_ttl=2000,
        auto_ack=False,
        exclusive=False
    )
]


manager.exchanges = [
    chains := Exchange(
        name='chains',
        exchange_type='direct',
        durable=False
    )
]


manager.bindings = [
    Binding(
        exchange=chains,
        queue=chain1,
        routing_key='chain1'
    ),
    Binding(
        exchange=chains,
        queue=chain2,
        routing_key='chain2'
    ),
    Binding(
        exchange=chains,
        queue=chain3,
        routing_key='chain3'
    ),
    Binding(
        exchange=chains,
        queue=chain4,
        routing_key='chain4'
    ),
    Binding(
        exchange=chains,
        queue=chain5,
        routing_key='chain5'
    ),
]


@manager.consume(queue_name=settings.CHAIN_ROUTING_KEY)
async def chain1_complete_callback(message: Message, exchange: Exchange, **_):
    data = await message.get_data()
    channel = message.channel

    await message.ack()

    logger.info(msg=f'Получено по ключу маршрутизации "{settings.CHAIN_ROUTING_KEY}": {data}')

    await exchange.send_message(
        channel=channel,
        routing_key=settings.NEXT_CHAIN_ROUTING_KEY,
        message=data
    )

    return logger.info(msg=f'Отправлено на ключ маршрутизации "{settings.NEXT_CHAIN_ROUTING_KEY}": {data}')


if __name__ == '__main__':
    manager.start()
