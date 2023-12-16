import os

# Директория проекта
BASE_DIR = os.path.dirname(__file__)

# Папка с шаблонами для FastAPI
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

# Ключ маршрутизации для очереди RabbitMQ для данного chain
CHAIN_ROUTING_KEY = os.getenv('CHAIN_ROUTING_KEY', 'chain1')

# Ключ маршрутизации для следующей очереди RabbitMQ
# на которую данный chain будет отправлять обработанные данные
NEXT_CHAIN_ROUTING_KEY = os.getenv('NEXT_CHAIN_ROUTING_KEY', 'chain2')

# Хост, на котором будет работать интерфейс FastAPI
HOST = os.getenv('HOST', 'localhost')

# Порт, на котором будет работать интерфейс FastAPI
PORT = os.getenv('PORT', 8080)

# Хост, на котором запущена СУБД
DATABASE_CONNECTION_URI = os.getenv('DATABASE_CONNECTION_URI', 'root:1234@localhost:3306')

# Драйвер СУБД для подключения через SqlAlchemy
# Доступные драйвера: sqlite, mysql+pymysql, postgresql+psycopg2
DATABASE_DRIVER = os.getenv('DATABASE_DRIVER', 'mysql+pymysql')


# Схема БД, на которой будут храниться данные данного chain
DATABASE_SCHEME = os.getenv('DATABASE_SCHEME', CHAIN_ROUTING_KEY)


# Адрес на подключение к RabbitMQ
BROKER_URL = os.getenv('BROKER_URL', 'amqp://guest:guest@localhost:5672')
