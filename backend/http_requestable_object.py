import json
import logging
import random
import requests
import time

from urllib.parse import urljoin

import utils
from exceptions.http_requestable_object import *


class HTTPRequestableObject():
    _BASE_URL: str = None
    _logger: logging.Logger = None

    def __init__(
            self,
            base_url=None,
            logger=logging.getLogger(__name__),
    ):
        if (base_url is None) or (base_url == ""):
            raise HTTPRequestableObjectBaseURLNotSpecified()
        else:
            self._BASE_URL = utils.normalize_url(base_url)

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

        endpoint_full_url = urljoin(self._BASE_URL, endpoint)

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
                        raise HTTPRequestableObjectUnsupportedMethod(method=method)

                return response

            except requests.exceptions.Timeout:
                self._logger.warning(f"Connection timeout. Retry number {retry} of {max_retries}.")

                retry += 1
                sleep = (1 + random.random()) * sleep
                time.sleep(sleep)

        raise HTTPRequestableObjectRequestTimeout(retry=retry, max_retries=max_retries)
