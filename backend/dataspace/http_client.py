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

        self._logger.info(f"Keys in config: {config.keys()}")
        self._logger.info(f"Token url: {config['token_url']}")
        if "token_url" in config and config["token_url"] is not None:
            self._logger.info("Using token authentication")
            token = self.obtain_token(config["token_url"], config["client_id"], config["username"], config["password"])
            self._http_client = httpx.Client(headers={"Authorization": f"Bearer {token}"})
        else:
            self._http_client = httpx.Client(auth=httpx.BasicAuth(config['username'], config['password']))

    def download_file(self, url, path_to_download: str | Path) -> str:
        self._logger.info(f"Downloading {url} into {str(path_to_download)}")

        path_to_download = Path(path_to_download)

        with self._http_client.stream("GET", url, timeout=10) as response:
            try:
                response.raise_for_status()
            except Exception as e:
                self._logger.error(f"Failed to download {url}: {e}")
                raise
            with open(path_to_download, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)

        return str(path_to_download)

    def obtain_token(self, token_url, client_id, username, password):
        # TODO - use refreshing, do not exchange token each request
        payload = {
            "client_id": client_id,
            "username": username,
            "password": password,
            "grant_type": "password"
        }
        response = httpx.post(token_url, data=payload)
        try:
            response.raise_for_status()
        except Exception as e:
            self._logger.error(f"Failed to obtain token {token_url}: {e}")
            raise
        return response.json()["access_token"]

