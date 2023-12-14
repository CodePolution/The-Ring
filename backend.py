from fastapi import FastAPI


FASTAPI_APP = FastAPI()


@FASTAPI_APP.get('setup/')
def setup_endpoint():
    return {
        'fields': [
            {'field1': 'int'},
            {'field2': 'int'},
            {'field3': 'int'},
            {'field4': 'int'}
        ]
    }


@FASTAPI_APP.post('setup/')
def setup_endpoint():
    pass