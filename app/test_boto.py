import boto3
from dotenv import load_dotenv
import os
import logging

# Загружаем переменные из .env файла
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

endpoint_url = os.environ.get('ENDPOINT_URL')
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
bucket_name = os.environ.get('S3_BUCKET_NAME')
region_name = os.environ.get('AWS_REGION', 'ru-central1') # default value

logger.info(f"ENDPOINT_URL: {endpoint_url}")
logger.info(f"AWS_ACCESS_KEY_ID: {aws_access_key_id}")
logger.info(f"AWS_SECRET_ACCESS_KEY: [hidden]")
logger.info(f"BUCKET_NAME: {bucket_name}")
logger.info(f"REGION_NAME: {region_name}")

s3 = boto3.client(
    's3',
    endpoint_url=endpoint_url,
    # endpoint_url=f's3://{endpoint_url.replace("https://", "")}',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name,
    verify=False  # Remove for production
)

try:
    response = s3.list_objects_v2(Bucket=bucket_name)
    logger.info("Успешное подключение к S3!")
    for obj in response.get('Contents', []):
        logger.info(obj['Key'])
except Exception as e:
    logger.error(f"Ошибка при подключении к S3: {e}")
