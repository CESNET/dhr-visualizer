import os

CDSE_CONNECTOR_S3 = {
    'host_base': os.getenv("CDSE_CONNECTOR_S3_HOST_BASE"),
    'host_bucket': os.getenv("CDSE_CONNECTOR_S3_HOST_BUCKET"),
    'region_name': os.getenv("CDSE_CONNECTOR_S3_REGION_NAME"),
    'access_key': os.getenv("CDSE_CONNECTOR_S3_ACCESS_KEY"),
    'secret_key': os.getenv("CDSE_CONNECTOR_S3_SECRET_KEY"),
}

DATAHUB_RELAY = {
    'host_base': os.getenv("DATAHUB_RELAY_HOST_BASE"),
    'username': os.getenv("DATAHUB_RELAY_USERNAME"),
    'password': os.getenv("DATAHUB_RELAY_PASSWORD"),
}
