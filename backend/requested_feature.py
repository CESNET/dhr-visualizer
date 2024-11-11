import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Any

from dataspace_stac import DataspaceSTAC
from s3_connector import S3Connector

from exceptions.requested_feature import *

from enums import RequestStatuses


class RequestedFeature():
    _logger: logging.Logger = None

    _feature_id: str = None
    _platform: str = None
    _filters: Dict[str, Any] = None

    _status: RequestStatuses = RequestStatuses.NON_EXISTING
    _href: str = None  # TODO možná url, Path, nebo tak něco..?

    _workdir: TemporaryDirectory = None
    _feature_dir: Path = None

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

        self._status = RequestStatuses.ACCEPTED
        self._logger.info(f"Processing status: {self._status}")

    def __del__(self):
        self._workdir.cleanup()

    def get_feature_id(self) -> str:
        return self._feature_id

    def get_status(self) -> RequestStatuses:
        return self._status

    def get_href(self) -> str:
        return self._href

    def generate_map_tile(self):
        # Todo Generovat tilu
        """
        Stažení tily identifikované pomocí feature_id z copernicus dataspace
        Pravděpodobně z jejich s3 na loklání uložiště. Poté spustit processing dané tily
        Po dokončení processingu zápis do DB ohledně dokončení generování

        Na stav se bude ptát peridociky forntend voláním /api/check_visualization_status
        """
        self._status = RequestStatuses.PROCESSING

        self._download_feature()

        print(f"Feature downloaded into {str(self._feature_dir)}")
        # v self._feature_dir nyní staženy data dané feature, destruktor self.__del__ složku smaže

        # Po vytvoření snímku ho dočasně nakopírovat na nějaké úložiště

        self.processing_status = RequestStatuses.COMPLETED

    def _get_s3_path(self) -> str:
        dataspace_stac = DataspaceSTAC(feature_id=self._feature_id)  # TODO add logger
        return dataspace_stac.get_s3_path()

    def _download_feature(self) -> Path:
        # TODO Need to create STAC search for given feature_id
        # https://documentation.dataspace.copernicus.eu/APIs/STAC.html
        # and then get 'S3Path' (s3 bucket_key) for this feature.

        bucket_key = self._get_s3_path()
        print(bucket_key)

        if '/eodata/' in bucket_key:
            bucket_key = bucket_key.replace('/eodata/', '')

        _s3_eodata = S3Connector(provider='eodata')
        self._feature_dir = _s3_eodata.download_file(bucket_key=bucket_key)

        if self._feature_dir is None:
            raise RequestedFeatureS3DownloadFailed(feature_id=self._feature_id)

        return self._feature_dir
