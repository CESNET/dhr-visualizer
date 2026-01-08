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


@router.post(f"{variables.UVICORN_SERVER_PREFIX}" + "/request_processing")
async def request_processing(
        processed_feature_model: ProcessedFeatureModel = ProcessedFeatureModel()
):
    logger.debug(f"[{__name__}]: request_feature_model: {processed_feature_model}")
    feature_id = processed_feature_model.feature_id

    # return failed reason once and prepare for recomputation
    db_feature = fastapi_shared.database.get(feature_id)
    if db_feature is not None and db_feature.get_status() == RequestStatuses.FAILED:
        fastapi_shared.database.delete(feature_id)
        raise HTTPException(
            status_code=500,
            detail=f"Feature processing failed! Reason: {db_feature.get_fail_reason()}"
        )

    if fastapi_shared.database.get(feature_id) is None:
        processed_feature: ProcessedFeature | None = None

        match Platforms(processed_feature_model.platform):
            case Platforms.SENTINEL_1:
                processed_feature = Sentinel1Feature(
                    feature_id=feature_id,
                    platform=processed_feature_model.platform,
                    filters=processed_feature_model.filters
                )

            case Platforms.SENTINEL_2:
                processed_feature = Sentinel2Feature(
                    feature_id=feature_id,
                    platform=processed_feature_model.platform,
                    filters=processed_feature_model.filters
                )

            case _:
                raise HTTPException(status_code=400, detail="Unknown platform!")

        fastapi_shared.database.set(
            key=feature_id,
            value=processed_feature
        )

        fastapi_shared.celery_queue.send_task('tasks.data_tasks.download_feature_task', args=[feature_id])

    return_entry: ProcessedFeature | None = fastapi_shared.database.get(feature_id)

    if return_entry is None:
        raise HTTPException(status_code=404, detail="Feature not found in database!")

    if return_entry.get_status == RequestStatuses.NON_EXISTING:
        fastapi_shared.database.delete(feature_id)
        raise HTTPException(status_code=404, detail="Feature not found in database!")

    if return_entry.get_status == RequestStatuses.FAILED:
        fastapi_shared.database.delete(feature_id)
        logger.error(f"[{__name__}]: Feature processing failed! Reason: {return_entry.get_fail_reason()}")
        raise HTTPException(
            status_code=500,
            detail=f"Feature processing failed! Reason: {return_entry.get_fail_reason()}"
        )

    return ReturnedFeatureModel(
        feature_id=return_entry.get_feature_id(),
        status=return_entry.get_status(),
        processed_files=return_entry.get_processed_files()
    )
