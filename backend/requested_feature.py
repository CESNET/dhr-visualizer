import logging

from abc import ABC, abstractmethod
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Any

from dataspace_odata import DataspaceOData
from s3_connector import S3Connector

from enums import RequestStatuses

from exceptions.requested_feature import *


class RequestedFeature(ABC):
    _logger: logging.Logger = None

    _feature_id: str = None
    _platform: str = None
    _filters: Dict[str, Any] = None

    _status: RequestStatuses = RequestStatuses.NON_EXISTING
    _href: str = None  # TODO možná url, Path, nebo tak něco..?

    _workdir: TemporaryDirectory = None

    def __init__(
            self, logger: logging.Logger = logging.getLogger(name=__name__),
            feature_id: str = None, platform: str = None, filters: Dict[str, Any] = None
    ):
        self._logger = logger

        if feature_id is None:
            raise RequestedFeatureIDNotSpecified()
        self._feature_id = feature_id

        if platform is not None:
            self._platform = platform

        if filters is not None:
            self._filters = filters

        self._workdir = TemporaryDirectory()

        self._set_status(status=RequestStatuses.ACCEPTED)
        self._logger.info(f"Processing status: {self.get_status()}")

    def __del__(self):
        self._workdir.cleanup()

    def get_feature_id(self) -> str:
        return self._feature_id

    def get_status(self) -> RequestStatuses:
        return self._status

    def _set_status(self, status: RequestStatuses):
        self._status = status

    def get_href(self) -> str:
        return self._href

    async def process_feature(self):
        """
        Stažení tily identifikované pomocí feature_id z copernicus dataspace
        Pravděpodobně z jejich s3 na loklání uložiště. Poté spustit processing dané tily
        Po dokončení processingu zápis do DB ohledně dokončení generování

        Na stav se bude ptát peridociky forntend voláním /api/check_visualization_status
        """
        self._set_status(status=RequestStatuses.PROCESSING)

        self._download_feature()

        print(f"RequestedFeature {self._feature_id} downloaded into {str(self._workdir.name)}")  # TODO proper logging
        # v self._feature_dir nyní staženy data dané feature, destruktor self.__del__ složku smaže

        # TODO Generovat snímky
        # self._generate_map_tile() # Predpokladam ze bude odlisne pro S1 i S2, tedy asi implementovat v sentinel1_feature.py a sentinel2_feature.py

        # Po vytvoření snímku ho dočasně nakopírovat na nějaké úložiště

        self._set_status(status=RequestStatuses.COMPLETED)

    def _get_s3_path(self) -> str:
        dataspace_stac = DataspaceOData(feature_id=self._feature_id)
        return dataspace_stac.get_s3_path()

    @abstractmethod
    def _filter_available_s3_files(self, available_files):
        pass

    def _download_feature(self):
        bucket_key = self._get_s3_path()

        if '/eodata/' in bucket_key:
            bucket_key = bucket_key.replace('/eodata/', '')

        s3_eodata_connector = S3Connector(provider='eodata')

        all_available_files = s3_eodata_connector.get_file_list(bucket_key=bucket_key)
        filtered_files = self._filter_available_s3_files(available_files=all_available_files)

        for file in filtered_files:
            s3_eodata_connector.download_file(bucket_key=file, root_output_directory=Path(self._workdir.name))
