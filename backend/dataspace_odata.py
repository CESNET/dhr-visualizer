import json
import logging
import random
import time

import requests

from urllib.parse import urljoin

from exceptions.dataspace_odata import *


class DataspaceOData:
    _logger = None
    _feature_id = None

    _ODATA_BASE_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/"

    def __init__(
            self,
            feature_id=None,
            logger=logging.getLogger(__name__)
    ):
        if feature_id is None:
            raise DataspaceODataFeatureIdNotProvided()
        self._feature_id = feature_id

        self._logger = logger

    def _send_request(
            self,
            endpoint,
            headers=None,
            payload_dict=None,
            max_retries=5,
            method="GET"
    ) -> requests.Response:
        if headers is None:
            headers = {}

        if payload_dict is None:
            payload_dict = {}

        endpoint_full_url = urljoin(self._ODATA_BASE_URL, endpoint)

        response = self._retry_request(
            endpoint=endpoint_full_url, payload_dict=payload_dict,
            max_retries=max_retries, headers=headers, method=method
        )

        return response

    def _retry_request(
            self,
            endpoint,
            payload_dict,
            max_retries=5,
            headers=None,
            timeout=10,
            sleep=5,
            method="GET"
    ) -> requests.Response:
        if headers is None:
            headers = {}

        retry = 0
        while max_retries > retry:
            self._logger.info(f"Sending request to URL {endpoint}. Retry: {retry}")
            try:
                match method:
                    case "GET":
                        response = requests.get(
                            url=endpoint,
                            data=json.dumps(payload_dict),
                            headers=headers,
                            timeout=timeout
                        )

                    case "POST":
                        response = requests.post(
                            url=endpoint,
                            data=json.dumps(payload_dict),
                            headers=headers,
                            timeout=timeout
                        )

                    case "PUT":
                        response = requests.put(
                            url=endpoint,
                            data=json.dumps(payload_dict),
                            headers=headers,
                            timeout=timeout
                        )

                    case "DELETE":
                        response = requests.delete(
                            url=endpoint,
                            headers=headers,
                            timeout=timeout
                        )

                    case _:
                        raise DataspaceODataUnsupportedMethod(method=method)

                return response

            except requests.exceptions.Timeout:
                self._logger.warning(f"Connection timeout. Retry number {retry} of {max_retries}.")

                retry += 1
                sleep = (1 + random.random()) * sleep
                time.sleep(sleep)

        raise DataspaceODataRequestTimeout(retry=retry, max_retries=max_retries)

    def get_s3_path(self) -> str:
        endpoint = f"Products({self._feature_id})"

        response_content_dict = json.loads(self._send_request(endpoint=endpoint).content)
        return response_content_dict['S3Path']
