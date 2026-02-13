import logging
import random
import time

import httpx

from urllib.parse import urljoin

from dataspace.exceptions.http_requestable_object import *


class HTTPRequestableObject:
    _root_url: str = None
    _logger: logging.Logger = None

    def __init__(self, root_url=None,):
        if not root_url:
            raise HTTPRequestableObjectBaseURLNotSpecified()
        self._root_url = self._normalize_url(url=root_url)
        self._logger = logging.getLogger(__name__)

    @staticmethod
    def _normalize_url(url: str) -> str:
        from urllib.parse import urlparse
        return url if urlparse(url).path else url + "/"

    def _send_request(
            self, endpoint, headers=None, payload_dict=None, max_retries=5, method="GET"
    ) -> httpx.Response:
        headers = headers or {}
        payload_dict = payload_dict or {}

        endpoint_full_url = urljoin(self._root_url, endpoint)

        response = self._retry_request(
            endpoint=endpoint_full_url,
            payload_dict=payload_dict,
            max_retries=max_retries,
            headers=headers,
            method=method,
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
            method="GET",
    ) -> httpx.Response:
        headers = headers or {}

        retry = 0
        while retry < max_retries:
            self._logger.info(f"Sending request to URL {endpoint}. Retry: {retry}")

            try:
                with httpx.Client(timeout=timeout) as client:
                    match method.upper():
                        case "GET":
                            response = client.get(endpoint, params=payload_dict, headers=headers)
                        case "POST":
                            response = client.post(endpoint, json=payload_dict, headers=headers)
                        case "PUT":
                            response = client.put(endpoint, json=payload_dict, headers=headers)
                        case "DELETE":
                            response = client.delete(endpoint, headers=headers)
                        case _:
                            raise HTTPRequestableObjectUnsupportedMethod(method=method)

                    return response

            except httpx.TimeoutException:
                self._logger.warning(f"Connection timeout. Retry {retry + 1} of {max_retries}.")
                retry += 1
                time.sleep((1 + random.random()) * sleep)

        raise HTTPRequestableObjectRequestTimeout(retry=retry, max_retries=max_retries)
