import os

DHR__USE_DHR: bool = os.environ.get("DHR__USE_DHR", default="False").lower() in ["1", "true", "yes", ]
DHR__CATALOG_ROOT: str = os.getenv("DHR__CATALOG_ROOT")

CDSE__CATALOG_ROOT: str = os.getenv("CDSE__CATALOG_ROOT")

BACKEND_OUTPUT_DIRECTORY: str = os.getenv("BACKEND_OUTPUT_DIRECTORY")
FRONTEND_OUTPUT_DIRECTORY: str = os.getenv("FRONTEND_OUTPUT_DIRECTORY")
