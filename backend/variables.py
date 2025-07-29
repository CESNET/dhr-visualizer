import os


# # Only for local debugging
# from dotenv import load_dotenv
# load_dotenv("../.env")

true_statements = ["1", "true", "yes", ]

APP__NAME: str = os.getenv("APP__NAME", default="dhr-visualizer")
APP__LOG_LEVEL: str = os.getenv("APP__LOG_LEVEL", default="INFO")

UVICORN__SERVER_HOST: str = os.environ.get("UVICORN__SERVER_HOST", default="0.0.0.0")
UVICORN__SERVER_PORT: int = int(os.environ.get("UVICORN__SERVER_PORT", default=8081))
UVICORN__SERVER_PREFIX: str = os.environ.get("UVICORN__SERVER_PREFIX", default="/api")

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

DOCKER_SHARED_DATA_DIRECTORY: str = os.getenv("DOCKER_SHARED_DATA_DIRECTORY", default="/data")

MONGO__URI: str = os.getenv("MONGO__URI")
MONGO__DB: str = os.getenv("MONGO__DB")
