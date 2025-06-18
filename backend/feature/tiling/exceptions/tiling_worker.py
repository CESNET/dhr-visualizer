from pathlib import Path


class TilingWorkerError(Exception):
    def __init__(self, message="Tiling Worker General Error!"):
        self.message = message
        super().__init__(self.message)


class TilingWorkerTileOutOfBounds(TilingWorkerError):
    def __init__(
            self,
            message="Requested tile is outside the image bounds!",
            request_hash=None, z=None, x=None, y=None
    ):
        if request_hash is None:
            self._message = message
        else:
            self._message = f"Requested tile is outside the image bounds. Request hash {request_hash}!"

        if z is not None and x is not None and y is not None:
            self._message = message + f" z={z}, x={x}, y={y}"

        super().__init__(self._message)


class TilingWorkerOutputFileIsDirectory(TilingWorkerError):
    def __init__(self, message="Output file of tiling worker is directory!", path: Path = None):
        if path is None:
            self._message = message
        else:
            self._message = f"Output file of tiling worker is directory! Path: {str(path)}!"

        super().__init__(self._message)
