from .request_processing import router as request_processing_router
from .get_tile import router as get_tile_router
from .request_download import router as download_band_router

fastapi_routes = [
    request_processing_router,
    get_tile_router,
    download_band_router,
]
