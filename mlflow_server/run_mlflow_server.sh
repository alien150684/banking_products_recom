# run_mlflow_server.sh
# запуск командой source ./mlflow_server/run_mlflow_server.sh

# echo "ENDPOINT_URL: $ENDPOINT_URL"
# echo "S3_BUCKET_NAME: $S3_BUCKET_NAME"

mlflow server \
  --backend-store-uri postgresql://$DB_DESTINATION_USER:$DB_DESTINATION_PASSWORD@$DB_DESTINATION_HOST:$DB_DESTINATION_PORT/$DB_DESTINATION_NAME\
  --registry-store-uri postgresql://$DB_DESTINATION_USER:$DB_DESTINATION_PASSWORD@$DB_DESTINATION_HOST:$DB_DESTINATION_PORT/$DB_DESTINATION_NAME\
  --default-artifact-root s3://$S3_BUCKET_NAME \
  --no-serve-artifacts