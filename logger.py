import settings
import os
import logging
from typing import Union
from datetime import datetime


LOGS_DIR = os.path.join(settings.BASE_DIR, 'logs')


class Logger:
    """
    Класс для логирования запросов.
    """

    LOG_EXTENSION = 'log'
    DATE_STRING = "%d_%m_%Y"

    @property
    def file_name(self):
        time = datetime.now()
        string_time = time.strftime(self.DATE_STRING)
        file_name = f"{string_time}.{self.LOG_EXTENSION}"
        return os.path.join(LOGS_DIR, file_name)

    @property
    def logger(self):
        logger = logging.Logger(name='chain_service')
        formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        logger.setLevel(logging.INFO)

        handler = logging.FileHandler(filename=self.file_name)
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

        return logger

    def debug(self, **kwargs):
        return self.logger.debug(**kwargs)

    def info(self, **kwargs):
        return self.logger.info(**kwargs)

    def error(self, **kwargs):
        return self.logger.error(**kwargs)

    def get_log_files(self):
        log_files = os.listdir(LOGS_DIR)
        return list(filter(lambda file: file.endswith(f'.{self.LOG_EXTENSION}'), log_files))

    def get_log_file(self, filename: str):
        log_files = self.get_log_files()
        assert filename in log_files, 'Данный лог-файл не найден.'

        return os.path.join(LOGS_DIR, filename)

    def get_log_file_for_date(self, date: Union[datetime, int]):
        if isinstance(date, int):
            date = datetime.fromtimestamp(date)

        string_time = date.strftime(self.DATE_STRING)
        file_name = f"{string_time}.{self.LOG_EXTENSION}"
        return self.get_log_file(file_name)
