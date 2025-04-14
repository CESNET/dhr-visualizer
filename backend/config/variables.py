import os

true_statements = ["1", "true", "yes", ]

DHR__USE_DHR: bool = os.getenv("DHR__USE_DHR", default="False").lower() in true_statements
DHR__CATALOG_ROOT: str = os.getenv("DHR__CATALOG_ROOT")
DHR__CONNECTOR_CREDENTIALS = {
    'host_base': os.getenv("DHR__CONNECTOR_HOST_BASE"),
    'username': os.getenv("DHR__CONNECTOR_USERNAME"),
    'password': os.getenv("DHR__CONNECTOR_PASSWORD"),
}

CDSE__CATALOG_ROOT: str = os.getenv("CDSE__CATALOG_ROOT")
CDSE__CONNECTOR_S3_CREDENTIALS = {
    'host_base': os.getenv("CDSE__CONNECTOR_S3_HOST_BASE"),
    'host_bucket': os.getenv("CDSE__CONNECTOR_S3_HOST_BUCKET"),
    'region_name': os.getenv("CDSE__CONNECTOR_S3_REGION_NAME"),
    'access_key': os.getenv("CDSE__CONNECTOR_S3_ACCESS_KEY"),
    'secret_key': os.getenv("CDSE__CONNECTOR_S3_SECRET_KEY"),
}

BACKEND_OUTPUT_DIRECTORY: str = os.getenv("BACKEND_OUTPUT_DIRECTORY")
FRONTEND_OUTPUT_DIRECTORY: str = os.getenv("FRONTEND_OUTPUT_DIRECTORY")
