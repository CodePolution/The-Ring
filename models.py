from pydantic import BaseModel, field_validator


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
            result = eval(test_value)
            print(result)
        except:
            raise RuntimeError(
                'Указанная функция работает некорректно.'
            )

        return value


class FieldModel(BaseModel):
    """
    Подмодель для выввода данных полей из сообщения
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
