import sqlalchemy
from sqlalchemy.orm import DeclarativeBase


class DBModel(DeclarativeBase):
    """
    Базовая модель БД
    """


class FieldSetupModel(DBModel):
    __tablename__ = ''
