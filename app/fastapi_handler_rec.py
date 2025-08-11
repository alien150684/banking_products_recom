from dotenv import load_dotenv
import logging
import os
import pandas as pd

# Настроим базовое логирование, чтобы INFO-сообщения выводились в консоль
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.error")

# Загружаем переменные из .env файла
load_dotenv()

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

"""Класс Recommendations, который обрабатывает запросы API."""

class Recommendations:

    def __init__(self):

        self._recs = {"personal": None, 
                      "default": None}
        self._stats = {
            "request_personal_count": 0,
            "request_default_count": 0,
        }
        self.rec_type = None

    def load(self, type, path, **kwargs):
        """
        Загружает рекомендации из файла
        """

        logger.info(f"Loading recommendations, type: {type}")
        self._recs[type] = pd.read_parquet(path, **kwargs)
        if type == "personal":
            self._recs[type] = self._recs[type].set_index("user_id")
        logger.info(f"Loaded!")

    def get(self, user_id: int, k: int=100):
        """
        Возвращает список рекомендаций для пользователя
        """
        try:
            recs = self._recs["personal"].loc[user_id]
            recs = recs["item_id"].to_list()[:k]
            self._stats["request_personal_count"] += 1
            self.rec_type = "personal"
        except KeyError:
            recs = self._recs["default"]
            recs = recs["item_id"].to_list()[:k]
            self._stats["request_default_count"] += 1
            self.rec_type = "default"
        except:
            logger.error("No recommendations found!")
            recs = []

        return recs

    def stats(self):

        logger.info("Stats for recommendations")
        for name, value in self._stats.items():
            logger.info(f"{name:<30} {value} ")

if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    # Создаём тестовый запрос
    rec_store = Recommendations()

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

    recs = rec_store.get(user_id=15889, k=5)
    print("Recommendations:", recs)