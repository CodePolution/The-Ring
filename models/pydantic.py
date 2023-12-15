import pydantic
from pydantic import BaseModel, field_validator, ConfigDict


class PydanticModel(BaseModel):
    pass


class EmptyModel(PydanticModel):
    """
    Базовая модель для вывода любого без исключения json-сообщения
    """

    model_config = ConfigDict(extra='allow')


class FieldSetupModel(PydanticModel):
    """
    Подмодель сообщения для ностройки
    обработки конкретного поля, полученного из ответа.
    """

    name: str = pydantic.Field(description='Имя поля')
    operation: str = pydantic.Field(description='Пайтон-операция')

    @field_validator('name')
    def name_validation(cls, value):
        value = value.lower()
        assert value.isidentifier(), \
            'Название поля ввода должно сходиться с'\
            'форматом имени переменных в Python.'

        return value

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

    fields: list[FieldSetupModel] = pydantic.Field(description='Поля настройки')

    @field_validator('fields')
    def fields_validation(cls, value):
        assert len(value) >= 1, 'Минимальное кол-во полей для настроек - 1.'
        return value


class FieldModel(PydanticModel):
    """
    Подмодель для вывода данных полей из сообщения
    """

    name: str = pydantic.Field(description='Имя поля')
    value: int = pydantic.Field(description='Значение поля')

    @field_validator('name')
    def name_validation(cls, value):
        value = value.lower()
        assert value.isidentifier(), \
            'Название поля ввода должно сходиться с' \
            'форматом имени переменных в Python.'

        return value


class DataModel(PydanticModel):
    """
    Стандартная модель ответа сервера через RabbitMQ.
    """

    already_modified_fields: list[list[FieldModel]] = pydantic.Field(description='Уже обработанные поля', default=[])
    fields: list[FieldModel] = pydantic.Field(description='Поля ввода для обработки')

    def operate_fields(self, setups: list):
        setups_fields = {setup[0].name: setup[0].operation for setup in setups}

        for field in self.fields:
            if field.name in setups_fields:
                x = field.value
                operation = setups_fields[field.name].replace('x', str(x))
                field.value = eval(operation)

        if self.already_modified_fields is None:
            self.already_modified_fields = []

        self.already_modified_fields.append(self.fields)

        return self


