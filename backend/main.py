import logging

import uvicorn

import variables as env

from fastapi_server.fastapi_server import FastAPIServer

if __name__ == "__main__":
    fastapi_server = FastAPIServer(logger=logging.getLogger("uvicorn.error"))
    uvicorn.run(fastapi_server.get_app(), host=env.UVICORN__SERVER_HOST, port=env.UVICORN__SERVER_PORT)
