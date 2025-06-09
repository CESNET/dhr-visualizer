from fastapi import APIRouter, BackgroundTasks, HTTPException

from fastapi_server import fastapi_shared

from resources.enums import *
from resources.reqeusted_feature_model import RequestedFeatureModel
from resources.returned_feature_model import ReturnedFeatureModel

from feature.requested_feature import RequestedFeature
from feature.sentinel1_feature import Sentinel1Feature
from feature.sentinel2_feature import Sentinel2Feature

router = APIRouter()

@router.post("/api/request_visualization")
async def request_visualization(
        background_tasks: BackgroundTasks,
        requested_feature_model: RequestedFeatureModel = RequestedFeatureModel()
):
    fastapi_shared.logger.debug(f"[{__name__}]: request_feature_model: {requested_feature_model}")

    request_hash = requested_feature_model.hash_myself()
    fastapi_shared.logger.debug(f"[{__name__}]: request_hash: {request_hash}")

    # TODO - tady by se spíš měl zahashovat celý request a ten uložit do DB
    if fastapi_shared.database.get(request_hash) is None:
        requested_feature: RequestedFeature | None = None

        match Platforms(requested_feature_model.platform):
            case Platforms.SENTINEL_1:
                requested_feature = Sentinel1Feature(
                    logger=fastapi_shared.logger,
                    feature_id=requested_feature_model.feature_id,
                    platform=requested_feature_model.platform,
                    filters=requested_feature_model.filters,
                    request_hash=request_hash
                )

            case Platforms.SENTINEL_2:
                requested_feature = Sentinel2Feature(
                    logger=fastapi_shared.logger,
                    feature_id=requested_feature_model.feature_id,
                    platform=requested_feature_model.platform,
                    filters=requested_feature_model.filters,
                    request_hash=request_hash
                )

            case _:
                raise HTTPException(status_code=400, detail="Unknown platform!")

        # TODO zmenit praci s DB, je blbost ukladat tam Python object, ze jo...
        fastapi_shared.database.set(
            key=request_hash,
            value=requested_feature
        )

        background_tasks.add_task(requested_feature.process_feature)

    return_entry: RequestedFeature | None = fastapi_shared.database.get(request_hash)

    if return_entry is None:
        return HTTPException(status_code=404, detail="Feature not found in database!")

    if return_entry.get_status == RequestStatuses.NON_EXISTING:
        fastapi_shared.database.delete(request_hash)
        return HTTPException(status_code=404, detail="Feature not found in database!")

    if return_entry.get_status == RequestStatuses.FAILED:
        fastapi_shared.database.delete(request_hash)
        return HTTPException(status_code=500, detail="Feature processing failed!")

    return ReturnedFeatureModel(
        feature_id=return_entry.get_feature_id(),
        status=return_entry.get_status(),
        hrefs=return_entry.get_output_hrefs(),
    )