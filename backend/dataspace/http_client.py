import logging
import httpx

from pathlib import Path

from dataspace.exceptions.http_client import *


class HTTPClient:
    _logger = None

    _http_client: httpx.Client | None = None

    def __init__(
            self,
            config: dict = None,
            logger=logging.getLogger(__name__)
    ):
        self._logger = logger

        if config is None:
            raise HTTPClientConfigNotProvided()

        self._http_client = httpx.Client(auth=httpx.BasicAuth(config['username'], config['password']))

    def download_file(self, url, path_to_download: str | Path) -> str:
        print(f"Downloading {url} into {str(path_to_download)}")  # Todo logging

        path_to_download = Path(path_to_download)

        with self._http_client.stream("GET", url, timeout=10) as response:
            response.raise_for_status()
            with open(path_to_download, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)

        return str(path_to_download)
