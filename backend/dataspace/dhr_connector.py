import logging
import re

import httpx

from config.variables import DHR_CATALOG_ROOT
from dataspace.dataspace_connector import DataspaceConnector
from dataspace.exceptions.dhr_connector import *


class DHRConnector(DataspaceConnector):
    _resto_id: str | None = None

    def __init__(self, feature_id=None, logger: logging.Logger = logging.getLogger(__name__)):
        super().__init__(root_url=DHR_CATALOG_ROOT, feature_id=feature_id, logger=logger)

    def _get_resto_id(self) -> str:
        if self._resto_id is None:
            import uuid
            resto_uuid_namespace = b'\x92\x70\x80\x59\x20\x77\x45\xa3\xa4\xf3\x1e\xb4\x28\x78\x9c\xff'
            self._resto_id = str(uuid.uuid5(uuid.UUID(bytes=resto_uuid_namespace), f"dhr1{self._feature_id}"))

        return self._resto_id

    def _get_feature(self) -> dict:
        if self._feature is None:
            response: httpx.Response = self._send_request(endpoint="search", payload_dict={"ids": self._get_resto_id()})

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

        re_matches = re.findall(r"Nodes\('([^']+)'\)", full_path)
        asset_path = "/".join(re_matches)

        return asset_path

    def get_available_files(self) -> list[tuple[str, str]]:
        self._get_feature()

        available_files = [
            (self._get_asset_path(asset['href']), asset['href']) for asset in self._feature['assets'].values()
        ]

        return available_files
