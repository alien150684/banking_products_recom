import os
import time
import pandas as pd
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv(dotenv_path="./services/.env")
PORT = os.environ.get('MAIN_APP_PORT')
URL = f'http://localhost:{PORT}/api/price/'

test_data_df = pd.read_csv('test_data.csv')

# Получаем список столбцов с типом int64
int64_cols = test_data_df.select_dtypes('int64').columns
# Преобразуем типы столбцов int64 в int
test_data_df[int64_cols] = test_data_df[int64_cols].astype('int')

input_features = [
  "category_floor",
  "kitchen_area",
  "living_area",
  "total_area",
  "rooms",
  "is_apartment",
  "studio",
  "build_year",
  "building_type_int",
  "distance",
  "ceiling_height",
  "has_elevator"
]

for i in range(test_data_df.shape[0]):
    # Создаем словари c данными для отправки
    input_data = test_data_df.iloc[i].loc[input_features].to_dict()
    params = {'user_id': str(test_data_df.iloc[i].loc['id'])}
    print(f'request {i}')
    if i % 10 == 0:
        time.sleep(10)
    else:
       time.sleep(2)
    response = requests.post(URL, 
                            json=input_data, 
                            params=params)
    # print(response.text)
