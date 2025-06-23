import logging

import variables as env

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi_server import fastapi_shared
from fastapi_server.routes import fastapi_routes

from database.dict_database_connector import DictDatabaseConnector


class FastAPIServer:
    _fastapi_app: FastAPI = None

    def __init__(self, logger=logging.Logger(env.APP__NAME)):
        fastapi_shared.logger = logger
        fastapi_shared.logger.setLevel(env.APP__LOG_LEVEL.upper())
        fastapi_shared.database = DictDatabaseConnector()

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
