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

        # TODO V TOMLHE MISTE TO NEKDY PADNE:
        """
        REQUEST_VISUALIZATION>>>feature_id='b43f0086-6fec-4dcd-a3f8-a0661327c59f' platform='SENTINEL-2' filters={'cloud_cover': '100', 'levels': ['S2MSI2A'], 'bands': ['TCI']}<<<REQUEST_VISUALIZATION
        INFO:     93.91.154.133:56378 - "POST /api/request_visualization HTTP/1.1" 200 OK
        ERROR:    Exception in ASGI application
        Traceback (most recent call last):
        File "/usr/local/lib/python3.12/site-packages/httpx/_transports/default.py", line 101, in map_httpcore_exceptions
        yield
        File "/usr/local/lib/python3.12/site-packages/httpx/_transports/default.py", line 250, in handle_request
        resp = self._pool.handle_request(req)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/local/lib/python3.12/site-packages/httpcore/_sync/connection_pool.py", line 256, in handle_request
        raise exc from None
        File "/usr/local/lib/python3.12/site-packages/httpcore/_sync/connection_pool.py", line 236, in handle_request
        response = connection.handle_request(
        ^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/local/lib/python3.12/site-packages/httpcore/_sync/connection.py", line 103, in handle_request
        return self._connection.handle_request(request)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/local/lib/python3.12/site-packages/httpcore/_sync/http11.py", line 136, in handle_request
        raise exc
        File "/usr/local/lib/python3.12/site-packages/httpcore/_sync/http11.py", line 106, in handle_request
        ) = self._receive_response_headers(**kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/local/lib/python3.12/site-packages/httpcore/_sync/http11.py", line 177, in _receive_response_headers
        event = self._receive_event(timeout=timeout)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/local/lib/python3.12/site-packages/httpcore/_sync/http11.py", line 217, in _receive_event
        data = self._network_stream.read(
        ^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/local/lib/python3.12/site-packages/httpcore/_backends/sync.py", line 126, in read
        with map_exceptions(exc_map):
        ^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/local/lib/python3.12/contextlib.py", line 158, in __exit__
        self.gen.throw(value)
        File "/usr/local/lib/python3.12/site-packages/httpcore/_exceptions.py", line 14, in map_exceptions
        raise to_exc(exc) from exc
        httpcore.ReadTimeout: The read operation timed out
        
        The above exception was the direct cause of the following exception:
        
        Traceback (most recent call last):
        File "/usr/local/lib/python3.12/site-packages/uvicorn/protocols/http/h11_impl.py", line 403, in run_asgi
        result = await app(  # type: ignore[func-returns-value]
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/local/lib/python3.12/site-packages/uvicorn/middleware/proxy_headers.py", line 60, in __call__
        return await self.app(scope, receive, send)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/local/lib/python3.12/site-packages/fastapi/applications.py", line 1054, in __call__
        await super().__call__(scope, receive, send)
        File "/usr/local/lib/python3.12/site-packages/starlette/applications.py", line 112, in __call__
        await self.middleware_stack(scope, receive, send)
        File "/usr/local/lib/python3.12/site-packages/starlette/middleware/errors.py", line 187, in __call__
        raise exc
        File "/usr/local/lib/python3.12/site-packages/starlette/middleware/errors.py", line 165, in __call__
        await self.app(scope, receive, _send)
        File "/usr/local/lib/python3.12/site-packages/starlette/middleware/cors.py", line 93, in __call__
        await self.simple_response(scope, receive, send, request_headers=headers)
        File "/usr/local/lib/python3.12/site-packages/starlette/middleware/cors.py", line 144, in simple_response
        await self.app(scope, receive, send)
        File "/usr/local/lib/python3.12/site-packages/starlette/middleware/exceptions.py", line 62, in __call__
        await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
        File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
        raise exc
        File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
        await app(scope, receive, sender)
        File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 714, in __call__
        await self.middleware_stack(scope, receive, send)
        File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 734, in app
        await route.handle(scope, receive, send)
        File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 288, in handle
        await self.app(scope, receive, send)
        File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 76, in app
        await wrap_app_handling_exceptions(app, request)(scope, receive, send)
        File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
        raise exc
        File "/usr/local/lib/python3.12/site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
        await app(scope, receive, sender)
        File "/usr/local/lib/python3.12/site-packages/starlette/routing.py", line 74, in app
        await response(scope, receive, send)
        File "/usr/local/lib/python3.12/site-packages/starlette/responses.py", line 160, in __call__
        await self.background()
        File "/usr/local/lib/python3.12/site-packages/starlette/background.py", line 41, in __call__
        await task()
        File "/usr/local/lib/python3.12/site-packages/starlette/background.py", line 26, in __call__
        await self.func(*self.args, **self.kwargs)
        File "/app/feature/requested_feature.py", line 138, in process_feature
        downloaded_files_paths = await self._download_feature()
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/app/feature/requested_feature.py", line 124, in _download_feature
        downloaded_files = self._dataspace_connector.download_selected_files(files_to_download=filtered_files)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/app/dataspace/dhr_connector.py", line 79, in download_selected_files
        downloaded_file_path = self._dhr_http_client.download_file(file_to_download[1], downloaded_file_path)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/app/dataspace/http_client.py", line 32, in download_file
        with self._http_client.stream("GET", url, timeout=10) as response:
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/local/lib/python3.12/contextlib.py", line 137, in __enter__
        return next(self.gen)
        ^^^^^^^^^^^^^^
        File "/usr/local/lib/python3.12/site-packages/httpx/_client.py", line 868, in stream
        response = self.send(
        ^^^^^^^^^^
        File "/usr/local/lib/python3.12/site-packages/httpx/_client.py", line 914, in send
        response = self._send_handling_auth(
        ^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/local/lib/python3.12/site-packages/httpx/_client.py", line 942, in _send_handling_auth
        response = self._send_handling_redirects(
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/local/lib/python3.12/site-packages/httpx/_client.py", line 979, in _send_handling_redirects
        response = self._send_single_request(request)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/local/lib/python3.12/site-packages/httpx/_client.py", line 1014, in _send_single_request
        response = transport.handle_request(request)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/local/lib/python3.12/site-packages/httpx/_transports/default.py", line 249, in handle_request
        with map_httpcore_exceptions():
        ^^^^^^^^^^^^^^^^^^^^^^^^^
        File "/usr/local/lib/python3.12/contextlib.py", line 158, in __exit__
        self.gen.throw(value)
        File "/usr/local/lib/python3.12/site-packages/httpx/_transports/default.py", line 118, in map_httpcore_exceptions
        raise mapped_exc(message) from exc
        httpx.ReadTimeout: The read operation timed out
        Downloading https://dhr1.cesnet.cz/odata/v1/Products('b43f0086-6fec-4dcd-a3f8-a0661327c59f')/Nodes('S2A_MSIL2A_20250411T100041_N0511_R122_T33UVR_20250411T171300.SAFE')/Nodes('GRANULE')/Nodes('L2A_T33UVR_A051199_20250411T100401')/Nodes('IMG_DATA')/Nodes('R10m')/Nodes('T33UVR_20250411T100041_TCI_10m.jp2')/$value into /tmp/tmphwy2lhzq/S2A_MSIL2A_20250411T100041_N0511_R122_T33UVR_20250411T171300.SAFE/GRANULE/L2A_T33UVR_A051199_20250411T100401/IMG_DATA/R10m/T33UVR_20250411T100041_TCI_10m.jp2
        REQUEST_VISUALIZATION>>>feature_id='b43f0086-6fec-4dcd-a3f8-a0661327c59f' platform='SENTINEL-2' filters={'cloud_cover': '100', 'levels': ['S2MSI2A'], 'bands': ['TCI']}<<<REQUEST_VISUALIZATION
        """
        with self._http_client.stream("GET", url, timeout=10) as response:
            response.raise_for_status()
            with open(path_to_download, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)

        return str(path_to_download)
