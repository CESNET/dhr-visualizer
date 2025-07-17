from fastapi import APIRouter, HTTPException
from fastapi_server import fastapi_shared
from fastapi.responses import FileResponse
from fastapi.logger import logger
from resources.enums import *

router = APIRouter()


@router.get("/download_band/{request_hash}/{band}")
async def download_band(request_hash: str, band: str):
    logger.debug(f"[{__name__}]: Requesting band download for hash: {request_hash}, band: {band}")

    return_entry = fastapi_shared.database.get(request_hash)

    if return_entry is None:
        raise HTTPException(status_code=404, detail="Product not found in database!")

    if return_entry.get_status() != RequestStatuses.COMPLETED:
        raise HTTPException(status_code=400, detail="Product processing is not completed!")

    processed_files = return_entry.get_processed_files()
    if band not in processed_files:
        raise HTTPException(status_code=404, detail=f"Band {band} not available for this product!")

    file_path = processed_files[band]
    logger.debug(f"[{__name__}]: File path: {file_path}")
    return FileResponse(path=file_path, filename=f"{request_hash}_{band}.tif")
