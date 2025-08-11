import logging

# from database.database_connector import DatabaseConnector

database = None
logger: logging.Logger | None = None
celery_queue = None
