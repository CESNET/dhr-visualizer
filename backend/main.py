import logging

import uvicorn
from fastapi import FastAPI, BackgroundTasks, HTTPException

from fastapi.middleware.cors import CORSMiddleware

from enums import *
from dict_database_connector import DictDatabaseConnector
from reqeusted_feature_model import RequestedFeatureModel
from requested_feature import RequestedFeature
from returned_feature_model import ReturnedFeatureModel

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
    if database.get(requested_feature_model.feature_id) is None:
        requested_feature = RequestedFeature(
            logger=logger,
            feature_id=requested_feature_model.feature_id,
            platform=requested_feature_model.platform,
            filters=requested_feature_model.filters
        )

        # TODO zmenit praci s DB, je blbost ukladat tam Python object, ze jo...
        database.set(
            key=requested_feature_model.feature_id,
            value=requested_feature
        )

        background_tasks.add_task(requested_feature.generate_map_tile)

    return_entry = database.get(requested_feature_model.feature_id)

    if return_entry is None:
        return HTTPException(status_code=404, detail="Feature not found in database!")

    if return_entry.get_status == RequestStatuses.NON_EXISTING:
        database.delete(requested_feature_model.feature_id)
        return HTTPException(status_code=404, detail="Feature not found in database!")

    if return_entry.get_status == RequestStatuses.FAILED:
        database.delete(requested_feature_model.feature_id)
        return HTTPException(status_code=500, detail="Feature processing failed!")

    return ReturnedFeatureModel(
        feature_id=return_entry.get_feature_id(),
        status=return_entry.get_status(),
        href=return_entry.get_href(),
    )


if __name__ == "__main__":
    logger = logging.getLogger(name="visualization_backend")
    database = DictDatabaseConnector()
    uvicorn.run(app, host="0.0.0.0", port=8000)
