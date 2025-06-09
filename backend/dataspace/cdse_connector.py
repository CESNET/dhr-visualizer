import logging
import re

import httpx

from variables import CDSE__CATALOG_ROOT, CDSE__CONNECTOR_S3_CREDENTIALS

from dataspace.dataspace_connector import DataspaceConnector
from dataspace.s3_client import S3Client

from dataspace.exceptions.cdse_connector import *


class CDSEConnector(DataspaceConnector):
    _cdse_s3_client: S3Client | None = None

    def __init__(
            self,
            feature_id=None, workdir=None,
            logger: logging.Logger = logging.getLogger(__name__)
    ):
        super().__init__(root_url=CDSE__CATALOG_ROOT, feature_id=feature_id, workdir=workdir, logger=logger)
        self._cdse_s3_client = S3Client(config=CDSE__CONNECTOR_S3_CREDENTIALS, logger=self._logger)

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

        available_files = self._cdse_s3_client.get_file_list(bucket_key=bucket_key)

        return [(self._get_asset_path(available_file), available_file) for available_file in available_files]

    def download_selected_files(self, files_to_download: list[tuple[str, str]]) -> list[str]:
        downloaded_files = []

        for file_to_download in files_to_download:
            downloaded_file_path = self._cdse_s3_client.download_file(
                bucket_key=file_to_download[1],
                root_output_directory=self._workdir
            )
            downloaded_files.append(str(downloaded_file_path))

        return downloaded_files

    def get_coordinates(self) -> list[list[float]]:
        return self._get_feature()['GeoFootprint']['coordinates'][0]
