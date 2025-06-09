import io

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse, Response

import fastapi_server.fastapi_shared as fastapi_shared

from feature.tiling.tiling_worker import TilingWorker
from feature.exceptions.tiling_worker import TilingWorkerTileOutOfBounds

router = APIRouter()


@router.get("/api/get_tile/{z}/{x}/{y}.jpg")
def get_tile(
        z: int, x: int, y: int,
        request_hash: str = Query(None, description="Request hash assigned by /api/request_processing endpoint"),
        selected_file: str = Query(None, description="User selected file (satellite band etc.)"),
):
    fastapi_shared.logger.debug(f"[{__name__}]: Requesting tiles for request {request_hash}; z:{z}, x:{x}, y:{y}")

    if request_hash is None or selected_file is None:
        fastapi_shared.logger.debug(
            f"[{__name__}]: Request hash {request_hash} or selected file {selected_file} not filled!"
        )
        return Response(status_code=400)

    tiling_worker = TilingWorker(
        processed_feature=fastapi_shared.database.get(request_hash),
        selected_file=selected_file,
        z=z, x=x, y=y,
        logger=fastapi_shared.logger
    )

    try:
        tile_img_bytes: io.BytesIO = tiling_worker.get_tile()
        tile_img_bytes.seek(0)
        return StreamingResponse(tile_img_bytes, media_type="image/jpeg")

    except TilingWorkerTileOutOfBounds:
        return Response(status_code=204)
