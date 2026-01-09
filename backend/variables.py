import os


# # Only for local debugging
# from dotenv import load_dotenv
# load_dotenv("../.env")

true_statements = ["1", "true", "yes", ]

APP_NAME: str = os.getenv("APP_NAME", default="Oculus")
APP_LOG_LEVEL: str = os.getenv("APP_LOG_LEVEL", default="INFO")

UVICORN_SERVER_HOST: str = os.environ.get("UVICORN_SERVER_HOST", default="0.0.0.0")
UVICORN_SERVER_PORT: int = int(os.environ.get("UVICORN_SERVER_PORT", default=8081))
UVICORN_SERVER_PREFIX: str = os.environ.get("UVICORN_SERVER_PREFIX")

DHR_USE_DHR: bool = os.getenv("DHR_USE_DHR", default="False").lower() in true_statements
DHR_CATALOG_ROOT: str = os.getenv("DHR_CATALOG_ROOT")
DHR_CONNECTOR_CREDENTIALS = {
    'host_base': os.getenv("DHR_CONNECTOR_HOST_BASE"),
    'username': os.getenv("DHR_CONNECTOR_USERNAME"),
    'password': os.getenv("DHR_CONNECTOR_PASSWORD"),
    'token_url': os.getenv("DHR_CONNECTOR_TOKEN_URL"),
    'client_id': os.getenv("DHR_CONNECTOR_CLIENT_ID"),
}

CDSE_CATALOG_ROOT: str = os.getenv("CDSE_CATALOG_ROOT")
CDSE_S3_CREDENTIALS = {
    'host_base': os.getenv("CDSE_CONNECTOR_S3_HOST_BASE"),
    'host_bucket': os.getenv("CDSE_CONNECTOR_S3_HOST_BUCKET"),
    'region_name': os.getenv("CDSE_CONNECTOR_S3_REGION_NAME"),
    'access_key': os.getenv("CDSE_CONNECTOR_S3_ACCESS_KEY"),
    'secret_key': os.getenv("CDSE_CONNECTOR_S3_SECRET_KEY"),
}

DOCKER_SHARED_DATA_DIRECTORY: str = os.getenv("DOCKER_SHARED_DATA_DIRECTORY")

MONGO_URI: str = os.getenv("MONGO_URI")
MONGO_DB: str = os.getenv("MONGO_DB")

CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND")
