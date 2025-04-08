import os

CDSE__CONNECTOR_S3_CREDENTIALS = {
    'host_base': os.getenv("CDSE__CONNECTOR_S3_HOST_BASE"),
    'host_bucket': os.getenv("CDSE__CONNECTOR_S3_HOST_BUCKET"),
    'region_name': os.getenv("CDSE__CONNECTOR_S3_REGION_NAME"),
    'access_key': os.getenv("CDSE__CONNECTOR_S3_ACCESS_KEY"),
    'secret_key': os.getenv("CDSE__CONNECTOR_S3_SECRET_KEY"),
}

DHR__CONNECTOR_CREDENTIALS = {
    'host_base': os.getenv("DHR__CONNECTOR_HOST_BASE"),
    'username': os.getenv("DHR__CONNECTOR_USERNAME"),
    'password': os.getenv("DHR__CONNECTOR_PASSWORD"),
}
