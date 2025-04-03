import json
import logging
import shutil
import subprocess

import docker

from abc import ABC, abstractmethod
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Any

from resources.enums import RequestStatuses

from dataspace.dataspace_connector import DataspaceConnector
from dataspace.exceptions.dataspace_connector import DataspaceConnectorCouldNotFetchFeature
from dataspace.cdse_connector import CDSEConnector
from dataspace.dhr_connector import DHRConnector

from config import variables

from feature.exceptions.requested_feature import *


class RequestedFeature(ABC):
    _logger: logging.Logger = None

    _request_hash: str = None

    _dataspace_connector: DataspaceConnector | None = None

    _feature_id: str = None
    _platform: str = None
    _filters: Dict[str, Any] = None

    _status: RequestStatuses = RequestStatuses.NON_EXISTING

    _output_directory: Path = None
    _output_hrefs: [str] = None  # TODO možná url, Path, nebo tak něco..?

    _workdir: TemporaryDirectory = None

    def __init__(
            self, logger: logging.Logger = logging.getLogger(name=__name__),
            feature_id: str = None, platform: str = None, filters: Dict[str, Any] = None,
            request_hash: str = None
    ):
        self._logger = logger
        self._request_hash = request_hash

        self._workdir = TemporaryDirectory()

        if feature_id is None:
            raise RequestedFeatureIDNotSpecified()
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
        try:
            self._dataspace_connector = DHRConnector(
                feature_id=self._feature_id, workdir=self._workdir, logger=self._logger
            )
        except DataspaceConnectorCouldNotFetchFeature:
            self._dataspace_connector = CDSEConnector(
                feature_id=self._feature_id, workdir=self._workdir, logger=self._logger
            )

    def get_feature_id(self) -> str:
        return self._feature_id

    def get_status(self) -> RequestStatuses:
        return self._status

    def _set_status(self, status: RequestStatuses):
        self._status = status

    def get_output_hrefs(self) -> list[str]:
        return self._output_hrefs

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
        self._set_status(status=RequestStatuses.PROCESSING)

        downloaded_files_paths = await self._download_feature()

        print(f"Feature ID {self._feature_id} downloaded into {str(self._workdir.name)}")  # TODO proper logging

        output_files_paths = self._generate_map_tiles(input_files=downloaded_files_paths)
        # Po vytvoření snímku ho dočasně nakopírovat na nějaké úložiště
        # TODO prozatím bude uloženo ve složce webserveru s frontendem (config/variables.py --- FRONTEND_ROOT_DIR)
        # ze seznamu souborů ve složce udělat seznam odkazů na webserver a uložit do self._hrefs: [str]
        self._generate_output_hrefs(filepaths=output_files_paths)

        self._set_status(status=RequestStatuses.COMPLETED)

    def _generate_map_tiles(self, input_files: list[str]) -> list[str] | None:
        file_list = ' '.join(input_files)

        # self._output_directory = Path(f"{variables.FRONTEND_WEBSERVER_ROOT_DIR}/output/{self._request_hash}")
        self._output_directory = Path(f"/data/output/{self._request_hash}")
        self._output_directory.mkdir(parents=True, exist_ok=True)

        for item in self._output_directory.iterdir():
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

        # processed_tiles_json = os.popen(f"gjtiff -q 82 -o {str(self._output_directory)} {file_list}").read()
        # processed_tiles = json.loads(processed_tiles_json)

        print("GENERATING MAP TILES 01")
        cmd = f"docker exec gjtiff_container gjtiff -q 82 -o {str(self._output_directory)} {file_list}"
        print("GENERATING MAP TILES 02")
        gjtiff_stdout = self._run_gjtiff_docker(input_files=input_files, output_directory=self._output_directory)
        print(json.loads(gjtiff_stdout))
        print("GENERATING MAP TILES 03")
        processed_tiles = json.loads(gjtiff_stdout)
        print("GENERATING MAP TILES 04")

        return processed_tiles

    def _run_gjtiff_docker(self, input_files: list[str] = None, output_directory: Path = _output_directory) -> str:
        print("RUN GJTIFF_DOCKER 01")
        if input_files is None:
            raise ValueError("No input files provided")  ## TODO Proper exception

        command = ["gjtiff", "-q", "82", "-o" f"{str(output_directory)}"] + [input_file for input_file in input_files]

        print(command)

        gjtiff_container = docker.from_env().containers.get("gjtiff_container")
        result = gjtiff_container.exec_run(command, stdout=True, stderr=True, tty=False)

        print("RUN GJTIFF_DOCKER 02")
        return result.output.decode('utf-8')

    def _generate_output_hrefs(self, filepaths: list[str]):
        self._output_hrefs = [
            filepath.replace(variables.FRONTEND_WEBSERVER_ROOT_DIR, '') for filepath in filepaths
        ]
