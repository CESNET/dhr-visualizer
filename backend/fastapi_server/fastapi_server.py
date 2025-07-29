import logging
import sys

import variables as env

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.logger import logger as fastapi_logger
from fastapi_server import fastapi_shared
from fastapi_server.routes import fastapi_routes

# from database.dict_database_connector import DictDatabaseConnector
from database.mongo_database_connector import MongoDatabaseConnector

class FastAPIServer:
    _fastapi_app: FastAPI = None

    def __init__(self, logger=logging.Logger(env.APP__NAME)):
        fastapi_logger.handlers = logger.handlers
        fastapi_logger.setLevel(env.APP__LOG_LEVEL.upper())

        # file_handler = logging.FileHandler("dhr-visualization.log")
        # file_handler.setLevel(env.APP__LOG_LEVEL.upper())
        # file_handler.setFormatter(logging.Formatter('%(levelname)s %(asctime)s - %(name)s:  %(message)s'))
        # fastapi_logger.addHandler(file_handler)

        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(env.APP__LOG_LEVEL.upper())
        stdout_handler.setFormatter(logging.Formatter('%(levelname)s %(asctime)s - %(name)s:  %(message)s'))
        fastapi_logger.addHandler(stdout_handler)

        fastapi_shared.database = MongoDatabaseConnector()
        fastapi_shared.database.connect()

        self._fastapi_app = FastAPI(title=env.APP__NAME)

        # TODO odebrat na produkci
        self._fastapi_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allows all origins
            allow_credentials=True,
            allow_methods=["*"],  # Allows all methods
            allow_headers=["*"],  # Allows all headers
        )

        self._register_routes()

    def _register_routes(self):
        for route in fastapi_routes:
            self._fastapi_app.include_router(route)

    def get_app(self) -> FastAPI:
        return self._fastapi_app
