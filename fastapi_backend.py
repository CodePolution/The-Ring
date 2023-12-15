import models.fastapi
import models.pydantic
import settings
import database
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from logger import Logger

FASTAPI_APP = FastAPI()
LOGGER = Logger()
TEMPLATES = Jinja2Templates(directory='templates')

TEMPLATES.env.globals['chain_name'] = settings.CHAIN_ROUTING_KEY
TEMPLATES.env.globals['next_chain_name'] = settings.NEXT_CHAIN_ROUTING_KEY


def render_error(request: Request, message: str, status_code: int = 400):
    return TEMPLATES.TemplateResponse(
        'error.html',
        {'request': request, 'error_message': message},
        status_code=status_code
    )


@FASTAPI_APP.get('/')
async def index(request: Request):
    return TEMPLATES.TemplateResponse(
        'index.html',
        {
            'request': request
        }
    )


@FASTAPI_APP.get('/logs/', response_class=HTMLResponse)
async def log_file_list(request: Request):
    page = request.query_params.get('page')
    if not page:
        return RedirectResponse(url=f"{FASTAPI_APP.url_path_for('log_file_list')}?page=1")

    elif not page.isdigit():
        error_message = 'Значение страницы должно быть целым числом.'
        return render_error(request, error_message)

    page = int(page)

    elements_per_page = 10

    if not page or page < 1:
        page = 1

    log_files = LOGGER.get_log_files()
    log_files = log_files[(page-1)*elements_per_page:page*elements_per_page]

    total_pages = len(log_files) // elements_per_page + 1
    next_page = page + 1 if total_pages >= page + 1 else 0
    previous_page = page - 1 if page > 1 else 0

    if page > total_pages:
        return RedirectResponse(url=f"{FASTAPI_APP.url_path_for('log_file_list')}?page={page-1}")

    return TEMPLATES.TemplateResponse(
        'logs.html',
        {
            'request': request,
            'files': log_files,
            'chain_name': settings.CHAIN_ROUTING_KEY,
            'total_pages': total_pages,
            'page': page,
            'next_page': next_page,
            'previous_page': previous_page
        }
    )


@FASTAPI_APP.get('/logs/{file_name}/')
async def log_file_download(request: Request, file_name: str):
    try:
        file_path = LOGGER.get_log_file(file_name)
        return FileResponse(path=file_path, filename=file_name)
    except:
        error_message = 'Данный файл не найден.'
        return render_error(request, error_message)


@FASTAPI_APP.post('/setup/')
async def setup_post_endpoint(request: Request, fields: models.fastapi.FieldSetupModel = Depends()):
    try:
        data = models.pydantic.FieldSetupModel.model_validate(fields.__dict__)
        database.FieldSetupModel.insert(**data.model_dump())
    except Exception as e:
        error_message = f'Данная форма введена некорректно.\n{e}'
        return render_error(request, error_message)

    return TEMPLATES.TemplateResponse(
        'setup_complete.html',
        {'request': request, 'fields': data}
    )


@FASTAPI_APP.get('/setup/')
async def setup_endpoint(request: Request):
    fields = models.pydantic.FieldSetupModel.model_fields
    saved_fields = database.FieldSetupModel.select_all()

    return TEMPLATES.TemplateResponse(
        'setup.html',
        {'request': request, 'fields': fields, 'saved_fields': saved_fields}
    )
