from celery import Celery

import env as env


def create_celery_app() -> Celery:
    celery = Celery(
        "tasks",
        broker=env.CELERY_BROKER_URL,
        backend=env.CELERY_RESULT_BACKEND,
        include=["tasks.data_tasks"],
    )
    return celery

celery_app = create_celery_app()