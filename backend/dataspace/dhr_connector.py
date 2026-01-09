import logging
import re

import httpx

from variables import DHR_USE_DHR, DHR_CATALOG_ROOT, DHR_CONNECTOR_CREDENTIALS

from dataspace.dataspace_connector import DataspaceConnector
from dataspace.http_client import HTTPClient

from dataspace.exceptions.dhr_connector import *


class DHRConnector(DataspaceConnector):
    _dhr_http_client: HTTPClient | None = None

    def __init__(
            self,
            feature_id=None, workdir=None,
            logger: logging.Logger = logging.getLogger(__name__)
    ):
        if not DHR_USE_DHR:
            raise DHRConnectorIsNotRequestedByUser()
        super().__init__(root_url=DHR_CATALOG_ROOT, feature_id=feature_id, workdir=workdir, logger=logger)
        self._dhr_http_client = HTTPClient(config=DHR_CONNECTOR_CREDENTIALS, logger=self._logger)
        self._logger.info("DHR connector initialized")

    def _get_feature(self) -> dict:
        if self._feature is None:
            response: httpx.Response = self._send_request(endpoint="search", payload_dict={"ids": self._feature_id})

            if response.status_code != 200:
                raise DHRConnectorCouldNotFetchFeature(feature_id=self._feature_id)

            response_data = response.json()
            if response_data['numberReturned'] < 1:
                raise DHRConnectorCouldNotFetchFeature(feature_id=self._feature_id)

            if response_data['numberReturned'] > 1:
                raise DHRConnectorTooManyFeaturesReturned(returned=response_data['numberReturned'])

            self._feature = response_data['features'][0]

        return self._feature

    def _get_asset_path(self, full_path: str | None = None) -> str:
        if full_path is None:
            return ""

        self._logger.info(f"full path: {full_path}")
        self._logger.info(f"product: {re.search(r'/product/(.+?)/', full_path)}")
        parts = full_path.split('/product/')
        if len(parts) > 1:
            return parts[1]
        return ""

    def get_available_files(self) -> list[tuple[str, str]]:
        self._get_feature()

        available_files = [
            (self._get_asset_path(asset['href']), asset['href']) for asset in self._feature['assets'].values()
        ]
        self._logger.debug(f"Available files: {available_files}")

        return available_files

    def download_selected_files(self, files_to_download: list[tuple[str, str]]) -> list[str]:
        downloaded_files = []

        for file_to_download in files_to_download:
            downloaded_file_path = self._workdir.joinpath(file_to_download[0])
            downloaded_file_path.parent.mkdir(parents=True, exist_ok=True)
            downloaded_file_path = self._dhr_http_client.download_file(file_to_download[1], downloaded_file_path)
            downloaded_files.append(str(downloaded_file_path))

        return downloaded_files

    def get_polygon(self) -> list[list[float]]:
        return self._feature['geometry']['coordinates'][0]
