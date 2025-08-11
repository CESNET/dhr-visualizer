from fastapi import APIRouter, HTTPException
from fastapi_server import fastapi_shared

from fastapi.logger import logger

from resources.enums import *
from resources.reqeusted_feature_model import ProcessedFeatureModel
from resources.returned_feature_model import ReturnedFeatureModel

from feature.processing.processed_feature import ProcessedFeature
from feature.processing.sentinel1_feature import Sentinel1Feature
from feature.processing.sentinel2_feature import Sentinel2Feature

import variables as variables

router = APIRouter()


@router.post(f"{variables.UVICORN__SERVER_PREFIX}" + "/request_processing")
async def request_processing(
        processed_feature_model: ProcessedFeatureModel = ProcessedFeatureModel()
):
    logger.debug(f"[{__name__}]: request_feature_model: {processed_feature_model}")

    request_hash = processed_feature_model.hash_myself()
    logger.debug(f"[{__name__}]: request_hash: {request_hash}")

    # TODO - tady by se spíš měl zahashovat celý request a ten uložit do DB
    if fastapi_shared.database.get(request_hash) is None:
        processed_feature: ProcessedFeature | None = None

        match Platforms(processed_feature_model.platform):
            case Platforms.SENTINEL_1:
                processed_feature = Sentinel1Feature(
                    feature_id=processed_feature_model.feature_id,
                    platform=processed_feature_model.platform,
                    filters=processed_feature_model.filters,
                    request_hash=request_hash
                )

            case Platforms.SENTINEL_2:
                processed_feature = Sentinel2Feature(
                    feature_id=processed_feature_model.feature_id,
                    platform=processed_feature_model.platform,
                    filters=processed_feature_model.filters,
                    request_hash=request_hash
                )

            case _:
                raise HTTPException(status_code=400, detail="Unknown platform!")

        fastapi_shared.database.set(
            key=request_hash,
            value=processed_feature
        )

        fastapi_shared.celery_queue.send_task('tasks.data_tasks.process_feature_task', args=[processed_feature.get_feature_id()])

    return_entry: ProcessedFeature | None = fastapi_shared.database.get(request_hash)

    if return_entry is None:
        return HTTPException(status_code=404, detail="Feature not found in database!")

    if return_entry.get_status == RequestStatuses.NON_EXISTING:
        fastapi_shared.database.delete(request_hash)
        return HTTPException(status_code=404, detail="Feature not found in database!")

    if return_entry.get_status == RequestStatuses.FAILED:
        fastapi_shared.database.delete(request_hash)
        return HTTPException(
            status_code=500,
            detail=f"Feature processing failed! Reason: {return_entry.get_fail_reason()}"
        )

    return ReturnedFeatureModel(
        feature_id=return_entry.get_feature_id(),
        status=return_entry.get_status(),
        processed_files=return_entry.get_processed_files()
    )
