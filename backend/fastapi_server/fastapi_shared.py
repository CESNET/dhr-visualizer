import logging

from database.database_connector import DatabaseConnector

database: DatabaseConnector | None = None
logger: logging.Logger | None = None
celery_queue = None
