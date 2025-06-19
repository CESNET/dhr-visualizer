import io

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import RedirectResponse, Response

import fastapi_server.fastapi_shared as fastapi_shared

from feature.tiling.tiling_worker import TilingWorker
from feature.tiling.exceptions.tiling_worker import TilingWorkerTileOutOfBounds

import variables as variables

router = APIRouter()


@router.get(f"{variables.UVICORN__SERVER_PREFIX}" + "/get_tile/{z}/{x}/{y}.jpg")
def get_tile(
        z: int, x: int, y: int,
        request_hash: str = Query(None, description="Request hash assigned by /api/request_processing endpoint"),
        selected_file: str = Query(None, description="User selected file (satellite band etc.)"),
):
    try:
        fastapi_shared.logger.debug(f"[{__name__}]: Requesting tiles for request {request_hash}; z:{z}, x:{x}, y:{y}")

        if request_hash is None or selected_file is None:
            fastapi_shared.logger.debug(
                f"[{__name__}]: Request hash {request_hash} or selected file {selected_file} not filled!"
            )
            return HTTPException(status_code=400, detail="Request hash or selected file not filled!")

        tiling_worker = TilingWorker(
            processed_feature=fastapi_shared.database.get(request_hash),
            selected_file=selected_file,
            z=z, x=x, y=y,
            logger=fastapi_shared.logger
        )

        tile_path = tiling_worker.save_tile()
        return RedirectResponse(str(tile_path))

    except TilingWorkerTileOutOfBounds:
        return Response(status_code=204)

    except Exception as e:
        return HTTPException(status_code=500, detail=f"Backend error, reason: {str(e)}")
