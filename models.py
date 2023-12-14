from pydantic import BaseModel, field_validator


class FieldSetupModel(BaseModel):
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
    name: str
    value: str

    @field_validator('value')
    def value_validation(cls, value):
        assert value.is_digit(), 'Значение не является числом.'
        return value


class DataModel(BaseModel):
    fields: list[FieldModel]
    message: str

    @field_validator('fields')
    def fields_validation(cls, value):
        assert len(value) <= 4, 'Указано меньше полей, чем нужно.'
        return value

