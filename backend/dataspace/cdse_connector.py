import logging
import re

import httpx

from config.variables import CDSE_CATALOG_ROOT
from config.variables_secret import CDSE_CONNECTOR_S3

from dataspace.dataspace_connector import DataspaceConnector
from dataspace.exceptions.cdse_connector import *

from dataspace.s3_connector import S3Connector


class CDSEConnector(DataspaceConnector):
    def __init__(self, feature_id=None, logger: logging.Logger = logging.getLogger(__name__)):
        super().__init__(root_url=CDSE_CATALOG_ROOT, feature_id=feature_id, logger=logger)

    def _get_feature(self) -> dict:
        if self._feature is None:
            endpoint = f"Products({self._feature_id})"

            response: httpx.Response = self._send_request(endpoint=endpoint)

            if response.status_code != 200:
                raise CDSEConnectorCouldNotFetchFeature(feature_id=self._feature_id)

            response_data = response.json()
            self._feature = response_data

        return self._feature

    def _get_s3_path(self) -> str:
        self._get_feature()

        try:
            return self._feature['S3Path']
        except KeyError:
            raise CDSEConnectorFeatureDoesNotContainS3Path(feature_id=self._feature_id)
        except Exception as e:
            raise e

    def _get_asset_path(self, full_path: str | None = None) -> str:
        re_match = re.search(re.escape(self._get_feature()['Name']), full_path)
        if re_match:
            asset_path = full_path[re_match.start():]  # Extract from match position to the end
            return asset_path
        else:
            return ""

    def get_available_files(self) -> list[tuple[str, str]]:
        bucket_key = self._get_s3_path()

        if '/eodata/' in bucket_key:
            bucket_key = bucket_key.replace('/eodata/', '')

        s3_eodata_connector = S3Connector(CDSE_CONNECTOR_S3)

        available_files = s3_eodata_connector.get_file_list(bucket_key=bucket_key)

        return [(self._get_asset_path(available_file), available_file) for available_file in available_files]
