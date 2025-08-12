
from dotenv import load_dotenv
import logging
import os
import random
import requests
import sys 
import time

# Настройка логгера
script_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
logger = logging.getLogger(script_name)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(f"{script_name}.log", encoding='utf-8')
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


# Загружаем переменные окружения из .env
load_dotenv()
PORT = os.environ.get('MAIN_APP_PORT')
URL = f'http://localhost:{PORT}'

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

# =============================================================================
# Добавим события взаимодействия пользователя с объектами для выдачи онлайн-рекомендаций:
# user_id = 15889 # "старый" пользователь
# user_id = 5555555555555555 # новый пользователь
# params = {"user_id": user_id, 'k': 5}

# =============================================================================

for i in range(500):
    # Создаем словарь c данными для отправки
    user_id = random.randint(15000, 1600000)
    params = {"user_id": user_id, 'k': 5}
    
    # Имитация времени обработки запроса
    time.sleep(random.randint(2, 10))
    resp = requests.post(URL + "/recommendations", 
                         headers=headers, 
                         params=params)
    
    recs = resp.json()
    recs_list = recs.get("recs")
    logger.info(f'request {i+1}: {params}')
    logger.info(f'recommendations: {recs_list}')
