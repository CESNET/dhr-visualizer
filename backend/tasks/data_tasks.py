from celery_app import celery_app
from database.mongo_database_connector import MongoDatabaseConnector
from celery.utils.log import get_task_logger

_db: MongoDatabaseConnector | None = None
logger = get_task_logger("tasks")

def init_db():
    global _db
    if _db is None:
        _db = MongoDatabaseConnector()
        _db.connect()


@celery_app.task(ignore_result=True)
def process_feature_task(feature_id: str):
    init_db()
    # will have more complex payload once we implement additional bands processing for existing files
    logger.info(f"Task {feature_id}")
    feature = _db.get(feature_id)
    feature._logger = logger
    logger.info(f"Processed feature: {feature}")
    feature.process_feature()
    _db.set(key=feature_id, value=feature)
