from celery_app import celery_app
from database.mongo_database_connector import MongoDatabaseConnector
from celery.utils.log import get_task_logger
from resources.enums import RequestStatuses

_db: MongoDatabaseConnector | None = None
logger = get_task_logger("tasks")

def init_db():
    global _db
    if _db is None:
        _db = MongoDatabaseConnector()
        _db.connect()

@celery_app.task(ignore_result=True)
def download_feature_task(feature_id: str):
    init_db()
    logger.info (f"Download task for {feature_id}")
    feature = _db.get(feature_id)
    feature._status = RequestStatuses.DOWNLOADING
    _db.set(key=feature_id, value=feature)

    feature.download_feature()
    _db.set(key=feature_id, value=feature)
    if feature.get_status() == RequestStatuses.PROCESSING:
        process_feature_task.delay(feature_id)

@celery_app.task(ignore_result=True)
def process_feature_task(feature_id: str):
    init_db()
    logger.info(f"Processing task for {feature_id}")
    feature = _db.get(feature_id)

    feature.process_feature()
    _db.set(key=feature_id, value=feature)

# todo - add cleaning task for downloaded files? for processed files?
