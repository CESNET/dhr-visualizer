import logging

import variables as env

from fastapi_server.fastapi_server import FastAPIServer

fastapi_server = FastAPIServer(logger=logging.getLogger(env.APP__NAME))
app = fastapi_server.get_app()