import logging
import uvicorn

from fastapi_server.fastapi_server import FastAPIServer
from celery import Celery

import variables as env

if __name__ == "__main__":
    celery_queue = Celery('tasks', broker=env.CELERY_BROKER_URL, backend=env.CELERY_RESULT_BACKEND)
    fastapi_server = FastAPIServer(celery_queue, logger=logging.getLogger(env.APP__NAME))
    uvicorn.run(fastapi_server.get_app(), host=env.UVICORN__SERVER_HOST, port=env.UVICORN__SERVER_PORT)
