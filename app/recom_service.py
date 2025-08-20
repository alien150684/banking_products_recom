# запуск
# uvicorn recom_service:app

from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi_handler_rec import Recommendations
import logging
import os
# "надстройка" prometheus_client для FastAPI
# готовая библиотека, загружающая экспортёр метрик в FastAPI-приложение
from prometheus_fastapi_instrumentator import Instrumentator
# базовый экспортёр для Python-скриптов
from prometheus_client import Counter 
# Counter — класс, отвечающий за метрики, которые относятся к типу "счётчик".
import requests
import uvicorn

"""Cервис выдачи рекомендаций"""
# ========================================================

logger = logging.getLogger("uvicorn.error")
logging.basicConfig(level=logging.info)

# ========================================================

# Параметры подключения к хранилищу S3
endpoint_url = os.environ.get('ENDPOINT_URL')  # https://storage.yandexcloud.net
bucket_name = os.environ.get('S3_BUCKET_NAME')  # s3-student-mle-20250226-e7b4c7010d
url = f's3://{bucket_name}'
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
storage_options={
        'key': aws_access_key_id,
        'secret': aws_secret_access_key,
        'client_kwargs': {'endpoint_url': endpoint_url}
    }

path4deafult_rec = os.environ.get('PATH_DEFAULT_REC')
path4personal_rec = os.environ.get('PATH_PERSONAL_REC')

# ========================================================

# Создаём обработчик запросов для API
rec_store = Recommendations()

# ========================================================

@asynccontextmanager
# Декоратор @asynccontextmanager позволяет создавать асинхронный контекстный менеджер — объект, который можно использовать с async with.
# В данном случае функция lifespan становится асинхронным контекстным менеджером.
async def lifespan(app: FastAPI):
    # код ниже (до yield) выполнится только один раз при запуске сервиса
    logger.info("Starting")

    # ========================================================

    # Создание пользовательских метрик с помощью Prometheus

    # request_personal_count — объект для сбора метрики
    app.state.request_personal_count = Counter(
        # имя метрики
        'request_personal_count', 
        # описание метрики
        'Number of request with personal recommendations'
    )

    # request_default_count — объект для сбора метрики
    app.state.request_default_count = Counter(
        # имя метрики
        'request_default_count', 
        # описание метрики
        'Number of request with default recommendations'
    )

    # ========================================================

    # Загрузка рекомендаций
    rec_store.load(
        type='personal',
        path=f'{url}/{path4personal_rec}',
        storage_options = storage_options,
        columns=["user_id", "item_id", "score"],
    )

    rec_store.load(
        type='default',
        path=f'{url}/{path4deafult_rec}',
        storage_options = storage_options,
        columns=["item_id", "score"],
    )

    logger.info("Ready!")
    # точка, где управление передаётся обратно FastAPI, и приложение начинает работать
    yield
    # этот код выполнится только один раз при остановке сервиса
    logger.info("Stopping")

# ========================================================

# Создаём приложение FastAPI
# Параметр lifespan=lifespan передаёт FastAPI функцию жизненного цикла, которую оно будет использовать.
# FastAPI вызовет этот контекстный менеджер при запуске и остановке приложения.
app = FastAPI(title="recommendations", lifespan=lifespan)

# ========================================================

# инициализируем и запускаем экпортёр метрик Prometheus
instrumentator = Instrumentator()
instrumentator.instrument(app)
instrumentator.expose(app)

# ========================================================

@app.post("/recommendations")
async def recommendations(user_id: int, k:int = 5):
    """
    Возвращает список рекомендаций длиной k для пользователя user_id
    """
   
    result = rec_store.get(user_id, k)
    recs = result.get("recs")
    rec_type = result.get("type")

    if rec_type == 'personal':
        # увеличиваем значение метрики на 1
        app.state.request_personal_count.inc()
    elif rec_type == 'default':
        # увеличиваем значение метрики на 1
        app.state.request_default_count.inc()

    # Проверка расчёта метрик
    # rec_store.stats()
    return {"recs": recs} 

# ========================================================

if __name__ == "__main__": 
    # Запускает приложение с использованием Uvicorn на указанном хосте и порту, с включенной опцией перезагрузки (reload) для разработки.
    uvicorn.run("recom_service:app", host="127.0.0.1", port=8000, reload=False)