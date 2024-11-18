import logging
import re

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict, Any

from dataspace_stac import DataspaceSTAC
from s3_connector import S3Connector

from enums import RequestStatuses

from exceptions.requested_feature import *


class RequestedFeature():
    _logger: logging.Logger = None

    _feature_id: str = None
    _platform: str = None
    _filters: Dict[str, Any] = None

    _filters_polarisation_channels_availability = None  # Todo stav tohohle po S3 filtrování nějak vracet frontendu, na frontendu pak vypsat alert

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

        self._filters_polarisation_channels_availability = {
            'VV': False,
            'VH': False,
            'HH': False,
            'HV': False
        }

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

        print(f"Feature downloaded into {str(self._workdir.name)}")
        # v self._feature_dir nyní staženy data dané feature, destruktor self.__del__ složku smaže

        # Po vytvoření snímku ho dočasně nakopírovat na nějaké úložiště

        self.processing_status = RequestStatuses.COMPLETED

    def _get_s3_path(self) -> str:
        dataspace_stac = DataspaceSTAC(feature_id=self._feature_id)
        return dataspace_stac.get_s3_path()

    def _prepare_channel_filter_array(self) -> list:
        polarisation_filter = []
        for channels_combine in self._filters['polarisation_channels_combined']:
            channels = channels_combine.split('+')
            polarisation_filter = polarisation_filter + channels

        for channel_separate in self._filters['polarisation_channels']:
            if channel_separate not in polarisation_filter:
                polarisation_filter.append(channel_separate)

        polarisation_filter = [channel.lower() for channel in polarisation_filter]
        return polarisation_filter

    def _filter_available_s3_files(self, available_files=None):
        if available_files is None:
            available_files = []

        polarisation_filter = self._prepare_channel_filter_array()

        filtered_files = []

        for available_file in available_files:
            if (
                    re.search('/preview/', available_file)
                    or re.search('.+-report-.+\.pdf', available_file)
            ):
                continue

            if (
                    re.search('/support/', available_file)
                    or re.search('manifest.safe', available_file)
            ):
                filtered_files.append(available_file)

            for polarisation_channel in polarisation_filter:
                if re.search(f'.+-{polarisation_channel}-.+', available_file):
                    filtered_files.append(available_file)
                    self._filters_polarisation_channels_availability[polarisation_channel.upper()] = True

        return filtered_files

    def _download_feature(self):
        bucket_key = self._get_s3_path()

        if '/eodata/' in bucket_key:
            bucket_key = bucket_key.replace('/eodata/', '')

        s3_eodata_connector = S3Connector(provider='eodata')

        all_available_files = s3_eodata_connector.get_file_list(bucket_key=bucket_key)
        filtered_files = self._filter_available_s3_files(available_files=all_available_files)

        for file in filtered_files:
            s3_eodata_connector.download_file(bucket_key=file, root_output_directory=Path(self._workdir.name))
