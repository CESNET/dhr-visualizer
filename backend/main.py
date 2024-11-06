import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any

from fastapi.middleware.cors import CORSMiddleware

from pathlib import Path

from enum import Enum

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


class RequestStatus(Enum):
    ACCEPTED = "accepted"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DatabaseEntries():
    FEATURE_ID = "feature_id"
    STATUS = "status"
    HREF = "href"


db = {}  # TODO Database needed


class ReqeustedFeature(BaseModel):
    feature_id: str = None
    platform: str = None
    filters: Dict[str, Any] = None
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

    def _update_db(self, status=None, href=None):
        if status is None:
            if db[self.feature_id][DatabaseEntries.STATUS]:
                status = db[self.feature_id][DatabaseEntries.STATUS]
            else:
                status = RequestStatus.FAILED

        if href is None:
            if db[self.feature_id][DatabaseEntries.HREF]:
                href = db[self.feature_id][DatabaseEntries.HREF]
            else:
                href = ""

        db[self.feature_id].update(
            {
                DatabaseEntries.FEATURE_ID: self.feature_id,
                DatabaseEntries.STATUS: status,
                DatabaseEntries.HREF: href
            }
        )

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

        self._update_db(status=RequestStatus.PROCESSING)

        # TODO _feature_dir udělat jako Tempfile.tempdir ...nebo jak přesně se ta knihovna jmenuje
        # Po vytvoření snímku ho dočasně nakopírovat na nějaké úložiště
        self._feature_dir = self._download_feature()
        print(f"Feature downloaded into {str(self._feature_dir)}")
        # v self._feature_dir nyní staženy data dané feature, destruktor self.__del__ složku smaže

        self._update_db(status=RequestStatus.COMPLETED)


@app.post("/api/request_visualization")
async def request_visualization(
        background_tasks: BackgroundTasks, requested_feature: ReqeustedFeature = ReqeustedFeature()
):
    if requested_feature.feature_id not in db:
        db[requested_feature.feature_id] = {
            DatabaseEntries.FEATURE_ID: requested_feature.feature_id,
            DatabaseEntries.STATUS: RequestStatus.ACCEPTED,
            DatabaseEntries.HREF: ""
        }
        background_tasks.add_task(requested_feature.start_map_tile_generation)

    return_entry = db[requested_feature.feature_id]
    if return_entry[DatabaseEntries.STATUS] == RequestStatus.FAILED:
        db.pop(requested_feature.feature_id)

    return return_entry


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
