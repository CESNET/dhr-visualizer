import logging

import json

from abc import ABC, abstractmethod
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Any

from dataspace.dataspace_connector import DataspaceConnector
from dataspace.exceptions.dataspace_connector import DataspaceConnectorCouldNotFetchFeature
from dataspace.cdse_connector import CDSEConnector
from dataspace.dhr_connector import DHRConnector

from dataspace_odata import DataspaceOData
from dataspace.s3_connector import S3Connector

from config import variables
from config import variables_secret
from enums import RequestStatuses

from exceptions.requested_feature import *


class RequestedFeature(ABC):
    _logger: logging.Logger = None

    _dataspace_connector: DataspaceConnector | None = None

    _feature_id: str = None
    _platform: str = None
    _filters: Dict[str, Any] = None

    _status: RequestStatuses = RequestStatuses.NON_EXISTING
    _hrefs: [str] = None  # TODO možná url, Path, nebo tak něco..?

    _workdir: TemporaryDirectory = None

    def __init__(
            self, logger: logging.Logger = logging.getLogger(name=__name__),
            feature_id: str = None, platform: str = None, filters: Dict[str, Any] = None
    ):
        self._logger = logger

        if feature_id is None:
            raise RequestedFeatureIDNotSpecified()
        self._feature_id = feature_id

        self._assing_connector()

        if platform is not None:
            self._platform = platform

        if filters is not None:
            self._filters = filters

        self._workdir = TemporaryDirectory()

        self._set_status(status=RequestStatuses.ACCEPTED)
        self._logger.info(f"Processing status: {self.get_status()}")

    def __del__(self):
        self._workdir.cleanup()

    def _assing_connector(self):
        try:
            self._dataspace_connector = DHRConnector(feature_id=self._feature_id, logger=self._logger)
        except DataspaceConnectorCouldNotFetchFeature:
            self._dataspace_connector = CDSEConnector(feature_id=self._feature_id, logger=self._logger)

    def get_feature_id(self) -> str:
        return self._feature_id

    def get_status(self) -> RequestStatuses:
        return self._status

    def _set_status(self, status: RequestStatuses):
        self._status = status

    def get_hrefs(self) -> list[str]:
        return self._hrefs

    def process_feature(self):
        """
        Stažení tily identifikované pomocí feature_id z copernicus dataspace
        Pravděpodobně z jejich s3 na loklání uložiště. Poté spustit processing dané tily
        Po dokončení processingu zápis do DB ohledně dokončení generování

        Na stav se bude ptát peridociky forntend voláním /api/check_visualization_status
        """
        self._set_status(status=RequestStatuses.PROCESSING)

        downloaded_files_paths = self._download_feature()

        print(f"RequestedFeature {self._feature_id} downloaded into {str(self._workdir.name)}")  # TODO proper logging

        output_files_paths = self._generate_map_tiles(input_files=downloaded_files_paths)
        # Po vytvoření snímku ho dočasně nakopírovat na nějaké úložiště
        # TODO prozatím bude uloženo ve složce webserveru s frontendem (config/variables.py --- FRONTEND_ROOT_DIR)
        # ze seznamu souborů ve složce udělat seznam odkazů na webserver a uložit do self._hrefs: [str]
        self._hrefs = self._prepare_hrefs(filepaths=output_files_paths)

        self._set_status(status=RequestStatuses.COMPLETED)

    def _get_s3_path(self) -> str:
        dataspace_stac = DataspaceOData(feature_id=self._feature_id)
        return dataspace_stac.get_s3_path()

    @abstractmethod
    def _filter_available_files(self, available_files: list[tuple[str, str]] = None) -> list[tuple[str, str]]:
        pass

    def _download_feature(self) -> list[str]:

        available_files = self._dataspace_connector.get_available_files()
        filtered_files = self._filter_available_files(available_files=available_files)

        downloaded_files_paths = []

        for file in filtered_files:
            fp = s3_eodata_connector.download_file(bucket_key=file, root_output_directory=Path(self._workdir.name))
            downloaded_files_paths.append(str(fp))

        return downloaded_files_paths

    def _generate_map_tiles(self, input_files: list[str]) -> list[str] | None:

        file_list = ' '.join(input_files)

        """
        # Format the date and time as a string
        output_directory = datetime.now().strftime(f"{variables.FRONTEND_WEBSERVER_ROOT_DIR}/output/%Y-%m-%d-%H:%M:%S")
        os.makedirs(output_directory, exist_ok=True)
        processed_tiles_json = os.popen(f"gjtiff -q 82 -o {output_directory} {file_list}").read()
        """

        processed_tiles_json = ''

        processed_tiles = json.loads(processed_tiles_json)
        return processed_tiles

    def _prepare_hrefs(self, filepaths: list[str]) -> list[str]:
        hrefs = []

        for filepath in filepaths:
            href = filepath.replace(variables.FRONTEND_WEBSERVER_ROOT_DIR, '')
            hrefs.append(href)

        return hrefs
