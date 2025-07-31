import json
import logging
import re
import shutil

import docker

from abc import ABC, abstractmethod
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Any

from fastapi_server import fastapi_shared
from resources.enums import RequestStatuses

from dataspace.dataspace_connector import DataspaceConnector
from dataspace.exceptions.dataspace_connector import DataspaceConnectorCouldNotFetchFeature
from dataspace.cdse_connector import CDSEConnector
from dataspace.dhr_connector import DHRConnector

import variables as variables

from feature.processing.exceptions.processed_feature import *


class ProcessedFeature(ABC):
    _logger: logging.Logger = None

    _request_hash: str = None

    _dataspace_connector: DataspaceConnector | None = None

    _feature_id: str = None
    _platform: str = None
    _filters: Dict[str, Any] = None

    _status: RequestStatuses = RequestStatuses.NON_EXISTING
    _fail_reason: str = None

    _output_directory: Path = None
    _output_files: list[str] = None  # TODO možná url, Path, nebo tak něco..?

    _bbox: list[float] = None

    _zoom_levels = {"min_zoom": 8, "max_zoom": 15} # todo should be like 8 to 15 but gjtiff crashes on low memory

    _workdir: TemporaryDirectory = None

    def __init__(
            self, logger: logging.Logger = logging.getLogger(name=__name__),
            feature_id: str = None, platform: str = None, filters: Dict[str, Any] = None,
            request_hash: str = None
    ):
        self._logger = logger
        self._logger.debug(f"[{__name__}]: Initializing Requested feature for platform: {platform}")

        self._request_hash = request_hash

        self._workdir = TemporaryDirectory()

        if feature_id is None:
            raise ProcessedFeatureIDNotSpecified()
        self._feature_id = feature_id

        self._assign_connector()

        if platform is not None:
            self._platform = platform

        if filters is not None:
            self._filters = filters

        self._set_status(status=RequestStatuses.ACCEPTED)
        self._logger.info(f"Processing status: {self.get_status()}")

    def _remove_path_tree(self, path: Path):
        for child in path.iterdir():
            if child.is_file():
                child.unlink()
            else:
                self._remove_path_tree(child)
        path.rmdir()

    def __del__(self):
        self._workdir.cleanup()
        # if self._output_directory is not None:
        #     self._remove_path_tree(self._output_directory)

    def _assign_connector(self):
        self._logger.debug(f"[{__name__}]: Assigning dataspace connector")

        if variables.DHR__USE_DHR:
            try:
                self._dataspace_connector = DHRConnector(
                    feature_id=self._feature_id,
                    workdir=self._workdir,
                    logger=self._logger
                )
                return
            except DataspaceConnectorCouldNotFetchFeature:
                pass

        self._dataspace_connector = CDSEConnector(
            feature_id=self._feature_id,
            workdir=self._workdir,
            logger=self._logger
        )

    def get_feature_id(self) -> str:
        return self._feature_id

    def get_status(self) -> RequestStatuses:
        return self._status

    def _set_fail_reason(self, reason):
        self._fail_reason = str(reason)

    def get_fail_reason(self) -> str:
        return self._fail_reason

    def _set_status(self, status: RequestStatuses):
        self._status = status

    def get_processed_files(self) -> dict[str, list[str]]:
        processed_files = {}

        if self._output_files is None:
            return processed_files

        for file in self._output_files:
            # file = file.replace(str(self._output_directory).replace("\\", "/"), '')
            file = file.split('/')[-1]

            processed_files.setdefault(self._request_hash, []).append(file)

        return processed_files

    def _set_bbox(self, bbox: list[float]):
        self._bbox = bbox

    def get_bbox(self) -> list[float]:
        if self._bbox is None:
            raise ProcessedFeatureBboxNotSet(feature_id=self._feature_id)
        return self._bbox

    def get_request_hash(self) -> str:
        return self._request_hash

    def to_dict(self) -> dict:
        return {
            "_id": self._request_hash,
            "feature_id": self._feature_id,
            "platform": self._platform,
            "filters": self._filters,
            "status": self._status.value,
            "fail_reason": self._fail_reason,
            "output_files": self._output_files,
            "bbox": self._bbox
        }

    @classmethod
    def from_dict(cls, data: dict):
        instance = cls(
            feature_id=data.get('feature_id'),
            platform=data.get('platform'),
            filters=data.get('filters'),
            request_hash=data.get('_id')
        )
        instance._status = RequestStatuses(data.get('status'))
        instance._fail_reason = data.get('fail_reason')
        instance._output_files = data.get('output_files')
        instance._bbox = data.get('bbox')
        return instance

    def get_output_directory(self) -> Path:
        if self._output_directory is None:
            raise ProcessedFeatureOutputDirectoryNotSet(feature_id=self._feature_id)

        return self._output_directory

    @abstractmethod
    def _filter_available_files(self, available_files: list[tuple[str, str]] = None) -> list[tuple[str, str]]:
        pass

    async def _download_feature(self) -> list[str]:
        available_files = self._dataspace_connector.get_available_files()
        filtered_files = self._filter_available_files(available_files=available_files)
        downloaded_files = self._dataspace_connector.download_selected_files(files_to_download=filtered_files)

        return downloaded_files

    async def process_feature(self):
        """
        Stažení tily identifikované pomocí feature_id z copernicus dataspace
        Pravděpodobně z jejich s3 na loklání uložiště. Poté spustit processing dané tily
        Po dokončení processingu zápis do DB ohledně dokončení generování

        Na stav se bude ptát peridociky forntend voláním /api/check_visualization_status
        """
        try:
            self._set_status(status=RequestStatuses.PROCESSING)

            self._set_bbox(self._dataspace_connector.get_rectangular_bbox())

            downloaded_feature_files_paths = await self._download_feature()

            self._logger.debug(f"[{__name__}]: Feature ID {self._feature_id} downloaded into {str(self._workdir.name)}")

            self._output_files = self._process_feature_files(feature_files=downloaded_feature_files_paths)
            # Po vytvoření snímku ho dočasně nakopírovat na nějaké úložiště
            # TODO prozatím bude uloženo ve složce webserveru s frontendem (config/variables.py --- FRONTEND_ROOT_DIR)
            # ze seznamu souborů ve složce udělat seznam odkazů na webserver a uložit do self._hrefs: [str]

            self._set_status(status=RequestStatuses.COMPLETED)
            fastapi_shared.database.set(self._request_hash, self)

        except Exception as e:
            self._fail_reason = str(e)
            self._set_status(status=RequestStatuses.FAILED)

    def _process_feature_files(self, feature_files: list[str]) -> list[str] | None:
        self._output_directory = Path(variables.DOCKER_SHARED_DATA_DIRECTORY, self._request_hash)
        self._output_directory.mkdir(parents=True, exist_ok=True)

        for item in self._output_directory.iterdir():
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

        gjtiff_stdout = self._run_gjtiff_docker(
            input_files=feature_files,
            output_directory=self._output_directory
        )
        self._logger.debug(f"[{__name__}]: gjtiff_stdout: |>|>|>{gjtiff_stdout}<|<|<|")

        processed_feature_files = self._extract_output_file_list(stdout=gjtiff_stdout)
        self._logger.debug(f"[{__name__}]: processed_feature_files: |>|>|>{processed_feature_files}<|<|<|")

        return processed_feature_files

    def _extract_output_file_list(self, stdout: str) -> list[str] | None:
        ## REMOVE TRAILING COMMAS - should be fixed in gjtiff # todo delete
        stdout = re.sub(r',\s*([]}])', r'\1', stdout)

        json_list_pattern = r'\[.*\]'
        matches = re.findall(json_list_pattern, stdout, re.DOTALL)
        last_json_list = json.loads(matches[-1] if matches else None)

        output_files = [item['outfile'] for item in last_json_list]

        return output_files

    def _run_gjtiff_docker(
            self,
            input_files: list[str] = None,
            output_directory: Path = _output_directory,
    ) -> str:
        if input_files is None:
            raise ValueError("No input files provided")  ## TODO Proper exception

        zoom_values = ",".join(str(z) for z in range(self._zoom_levels["min_zoom"], self._zoom_levels["max_zoom"] + 1))  # range max is exclusive
        command = ["gjtiff", "-q", "82", "-Q", "-z", zoom_values, "-o", str(output_directory)] + input_files

        self._logger.debug(f"[{__name__}]: Running gjtiff_docker command: {command}")

        gjtiff_container = docker.from_env().containers.get("oculus_gjtiff")

        stdout, stderr = gjtiff_container.exec_run(command, stdout=True, stderr=True, tty=False, demux=True).output

        if stderr:
            self._logger.error(f"[{__name__}]: gjtiff stderr: {stderr.decode('utf-8')}")

        return stdout.decode('utf-8')
