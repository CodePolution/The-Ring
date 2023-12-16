import settings
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, session
from sqlalchemy_utils import create_database, database_exists
from typing import Callable

connection_url = f"{settings.DATABASE_DRIVER}://{settings.DATABASE_CONNECTION_URI}/{settings.DATABASE_SCHEME}"

if not database_exists(connection_url):
    create_database(connection_url)


engine = sqlalchemy.create_engine(connection_url)
connection = engine.connect()
session = session.Session(connection)


class DBModel(DeclarativeBase):
    """
    Базовая модель БД
    """

    @classmethod
    def select_all(cls, *filters: Callable):
        return session.execute(
            sqlalchemy.select(cls).where(*filters)
        ).fetchall()

    @classmethod
    def select_one(cls, *filters: Callable):
        return session.execute(
            sqlalchemy.select(cls).where(*filters)
        ).fetchone()

    @classmethod
    def delete(cls, *filters: Callable):
        session.execute(
            sqlalchemy.delete(cls).where(*filters)
        )
        return session.commit()

    @classmethod
    def update(cls, *filters: Callable, **values):
        session.execute(
            sqlalchemy.update(cls).where(*filters).values(
                **values
            )
        )
        return session.commit()

    @classmethod
    def insert(cls, **values):
        session.execute(
            sqlalchemy.insert(cls).values(**values)
        )
        return session.commit()


class FieldSetupModel(DBModel):
    """
    Модель для хранения формул операций на поля
    """

    __tablename__ = 'field_setup_model'

    id = sqlalchemy.Column(
        sqlalchemy.Integer(),
        autoincrement=True,
        nullable=False,
        primary_key=True
    )

    name = sqlalchemy.Column(
        sqlalchemy.String(length=50),
        nullable=False,
        unique=True,
    )

    operation = sqlalchemy.Column(
        sqlalchemy.String(length=50),
        nullable=False
    )


DBModel.metadata.create_all(bind=connection)
