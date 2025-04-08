import logging

import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException

from fastapi.middleware.cors import CORSMiddleware

from database.dict_database_connector import (DictDatabaseConnector)

from resources.enums import *
from resources.reqeusted_feature_model import RequestedFeatureModel
from resources.returned_feature_model import ReturnedFeatureModel

from feature.requested_feature import RequestedFeature
from feature.sentinel1_feature import Sentinel1Feature
from feature.sentinel2_feature import Sentinel2Feature

app = FastAPI()

# TODO odebrat na produkci
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.post("/api/request_visualization")
async def request_visualization(
        background_tasks: BackgroundTasks,
        requested_feature_model: RequestedFeatureModel = RequestedFeatureModel()
):
    print(f"REQUEST_VISUALIZATION>>>{requested_feature_model}<<<REQUEST_VISUALIZATION")
    request_hash = requested_feature_model.hash_myself()

    # TODO - tady by se spíš měl zahashovat celý request a ten uložit do DB
    if database.get(request_hash) is None:
        requested_feature: RequestedFeature | None = None

        match Platforms(requested_feature_model.platform):
            case Platforms.SENTINEL_1:
                requested_feature = Sentinel1Feature(
                    logger=logger,
                    feature_id=requested_feature_model.feature_id,
                    platform=requested_feature_model.platform,
                    filters=requested_feature_model.filters,
                    request_hash=request_hash
                )

            case Platforms.SENTINEL_2:
                requested_feature = Sentinel2Feature(
                    logger=logger,
                    feature_id=requested_feature_model.feature_id,
                    platform=requested_feature_model.platform,
                    filters=requested_feature_model.filters,
                    request_hash=request_hash
                )

            case _:
                raise HTTPException(status_code=400, detail="Unknown platform!")

        # TODO zmenit praci s DB, je blbost ukladat tam Python object, ze jo...
        database.set(
            key=request_hash,
            value=requested_feature
        )

        background_tasks.add_task(requested_feature.process_feature)

    return_entry: RequestedFeature | None = database.get(request_hash)

    if return_entry is None:
        return HTTPException(status_code=404, detail="Feature not found in database!")

    if return_entry.get_status == RequestStatuses.NON_EXISTING:
        database.delete(request_hash)
        return HTTPException(status_code=404, detail="Feature not found in database!")

    if return_entry.get_status == RequestStatuses.FAILED:
        database.delete(request_hash)
        return HTTPException(status_code=500, detail="Feature processing failed!")

    return ReturnedFeatureModel(
        feature_id=return_entry.get_feature_id(),
        status=return_entry.get_status(),
        hrefs=return_entry.get_output_hrefs(),
    )


if __name__ == "__main__":
    logger = logging.getLogger(name="visualization_backend")
    database = DictDatabaseConnector()
    uvicorn.run(app, host="0.0.0.0", port=8081)
