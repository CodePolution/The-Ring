from pydantic import BaseModel, field_validator, ConfigDict
from pydantic.fields import ModelPrivateAttr, Field


class PydanticModel(BaseModel):
    @classmethod
    def get_field_names(cls, by_alias=False) -> list[str]:
        field_names = []
        for k, v in cls.__fields__.items():
            if by_alias and isinstance(v, ModelPrivateAttr):
                field_names.append(v.alias)
            else:
                field_names.append(k)

        return field_names


class EmptyModel(BaseModel):
    """
    Базовая модель для вывода любого без исключения json-сообщения
    """

    model_config = ConfigDict(extra='allow')


class FieldSetupModel(BaseModel):
    """
    Подмодель сообщения для ностройки
    обработки конкретного поля, полученного из ответа.
    """

    name: str
    operation: str

    @field_validator('operation')
    def function_validation(cls, value):
        value = value.lower()
        if not value:
            return 'x'

        assert 'x' in value, 'Обозначение X для числа не найдено.'

        try:
            x = 1
            test_value = value.replace('x', str(x))
            eval(test_value)
        except:
            raise RuntimeError(
                'Указанная функция работает некорректно.'
            )

        return value


class SetupModel(PydanticModel):
    """
    Модель для настройки списка полей
    """

    fields: list[FieldSetupModel]

    @field_validator('fields')
    def fields_validation(cls, value):
        assert len(value) >= 1, 'Минимальное кол-во полей для настроек - 1.'
        return value


class FieldModel(BaseModel):
    """
    Подмодель для вывода данных полей из сообщения
    """

    name: str
    value: int


class DataModel(BaseModel):
    """
    Стандартная модель ответа сервера через RabbitMQ.
    """

    fields: list[FieldModel] = None
    setups: list[FieldSetupModel] = None
    message: str

    @field_validator('fields')
    def fields_validation(cls, value):
        assert len(value) < cls.__param_count, \
            'Указано меньше полей, чем нужно.'\
            f'Укажите как минимум {cls.__param_count} полей.'
        return value

    @field_validator('setups')
    def setups_validation(cls, value):
        assert len(value) < cls.__param_count, \
            'Указано меньше настроек для полей, чем нужно.'\
            f'Укажите как минимум {cls.__param_count} параметра(ов).'
        return value
