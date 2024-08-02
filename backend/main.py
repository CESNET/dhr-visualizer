import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

from pathlib import Path

from dataspace_stac import DataspaceSTAC
from s3_connector import S3Connector

from exceptions.requested_feature import *

app = FastAPI()

# TODO odebrat na produkci
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

db = {}  # TODO Database needed


class ReqeustedFeature(BaseModel):
    feature_id: str = None
    _feature_dir: Path = None

    def __del__(self):
        if self._feature_dir is not None:
            self._delete_folder(path=self._feature_dir.parent)

    def _delete_folder(self, path: Path):
        for sub_path in path.iterdir():
            if sub_path.is_dir():
                self._delete_folder(sub_path)
            else:
                sub_path.unlink()
        path.rmdir()

    def _get_s3_path(self) -> str:
        dataspace_stac = DataspaceSTAC(feature_id=self.feature_id)  # TODO add logger
        return dataspace_stac.get_s3_path()

    def _download_feature(self) -> Path:
        # TODO Need to create STAC search for given feature_id
        # https://documentation.dataspace.copernicus.eu/APIs/STAC.html
        # and then get 'S3Path' (s3 bucket_key) for this feature.

        bucket_key = self._get_s3_path()
        if '/eodata/' in bucket_key:
            bucket_key = bucket_key.replace('/eodata/', '')

        _s3_eodata = S3Connector(provider='eodata')
        self._feature_dir = _s3_eodata.download_file(bucket_key=bucket_key)

        if self._feature_dir is None:
            raise RequestedFeatureS3DownloadFailed(feature_id=self.feature_id)

        return self._feature_dir

    def _update_db(self, status=None):
        if status is None:
            raise Exception  # Propper exception

        db[self.feature_id] = {
            "feature_id": self.feature_id,
            "status": status,
            "href": f"http://cesnet.cz/tile/{self.feature_id}"
        }

    def start_map_tile_generation(self):
        # Todo Generovat tilu
        """
        Stažení tily identifikované pomocí feature_id z copernicus dataspace
        Pravděpodobně z jejich s3 na loklání uložiště. Poté spustit processing dané tily
        Po dokončení processingu zápis do DB ohledně dokončení generování

        Na stav se bude ptát peridociky forntend voláním /api/check_visualization_status
        """
        if self.feature_id is None:
            raise RequestedFeatureIDNotSpecified()

        self._update_db(status="processing")

        self._feature_dir = self._download_feature()
        # v self._feature_dir nyní staženy data dané feature, destruktor self.__del__ složku smaže

        import time
        time.sleep(10)


@app.post("/api/request_visualization")
async def request_visualization(background_tasks: BackgroundTasks,
                                requested_feature: ReqeustedFeature = ReqeustedFeature()):
    db[requested_feature.feature_id] = {
        "feature_id": requested_feature.feature_id,
        "status": "processing",
        "href": ""
    }
    background_tasks.add_task(requested_feature.start_map_tile_generation)

    return db[requested_feature.feature_id]


@app.get("/api/check_visualization_status")
async def check_visualization_status(feature_id: str):
    if feature_id in db:
        return db[feature_id]
    else:
        return HTTPException(status_code=404, detail=f"{feature_id} not found!")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
