from fastapi import APIRouter, HTTPException
from pathlib import Path

import variables
from fastapi_server import fastapi_shared
from fastapi.responses import FileResponse
from fastapi.logger import logger
from resources.enums import *

router = APIRouter()


@router.get(variables.UVICORN_SERVER_PREFIX + "/download_image/{featureid}/{filename}")
async def download_image(featureid: str, filename: str):
    logger.debug(f"[{__name__}]: Requesting file download: {featureid}, file: {filename}")

    return_entry = fastapi_shared.database.get(featureid)

    if return_entry is None:
        raise HTTPException(status_code=404, detail="Product not found in database!")

    if return_entry.get_status() != RequestStatuses.COMPLETED:
        raise HTTPException(status_code=400, detail="Product processing is not completed!")

    processed_files = return_entry.get_processed_files()
    if filename not in processed_files[featureid]:
        raise HTTPException(status_code=404, detail=f"File {filename} not available for this product!")

    selected_file = (
            Path(variables.DOCKER_SHARED_DATA_DIRECTORY) /
            featureid /
            filename
    )

    logger.debug(f"[{__name__}]: File path: {selected_file}")
    return FileResponse(path=selected_file, filename=f"{featureid}_{filename}")
