import io
import logging

import mercantile
import numpy as np

from pathlib import Path

from PIL import Image

import variables
from feature.processing.processed_feature import ProcessedFeature

from feature.tiling.exceptions.tiling_worker import *


class TilingWorker:
    _logger: logging.Logger = None

    _processed_feature: ProcessedFeature = None

    _selected_file: str | Path = None
    _image_file: Image.Image = None
    _image_numpy: np.ndarray = None
    _image_width: float = None
    _image_height: float = None

    _z: int = None
    _x: int = None
    _y: int = None

    def __init__(
            self,
            processed_feature: ProcessedFeature,
            selected_file: str,
            z: int, x: int, y: int,
            logger: logging.Logger = logging.getLogger(__name__),
    ):
        self._logger = logger

        self._processed_feature = processed_feature

        self._selected_file = (
                Path(variables.BACKEND_OUTPUT_DIRECTORY) / self._processed_feature.get_request_hash() / selected_file
        )
        self._image_file = Image.open(self._selected_file)
        self._image_numpy = np.array(self._image_file)
        self._image_width, self._image_height = self._image_file.size

        self._z = z
        self._x = x
        self._y = y

    def _calculate_pixels_per_latlon(self):
        min_lon, min_lat, max_lon, max_lat = self._processed_feature.get_bbox()

        self._pixels_per_lon = self._image_width / (max_lon - min_lon)
        self._pixels_per_lat = self._image_height / (max_lat - min_lat)

    def _coords_to_pixel(self, lon, lat):
        min_lon, _, _, max_lat = self._processed_feature.get_bbox()
        self._calculate_pixels_per_latlon()

        pixel_x = int((lon - min_lon) * self._pixels_per_lon)
        pixel_y = int((max_lat - lat) * self._pixels_per_lat)

        return pixel_x, pixel_y

    def get_tile(self) -> io.BytesIO:
        tile_bounds = mercantile.bounds((self._x, self._y, self._z))
        self._logger.debug(f"[{__name__}]: Tile bounds: {tile_bounds}")

        left, top = self._coords_to_pixel(tile_bounds.west, tile_bounds.north)
        right, bottom = self._coords_to_pixel(tile_bounds.east, tile_bounds.south)

        if left > self._image_width or top > self._image_height or right < 0 or bottom < 0:
            raise TilingWorkerTileOutOfBounds(
                request_hash=self._processed_feature.get_request_hash(),
                z=self._z, x=self._x, y=self._y
            )

        tile_crop = self._image_file.crop((left, top, right, bottom))

        """
        try:
            tile_crop = image.crop((left, top, right, bottom))
        except (DecompressionBombWarning, DecompressionBombError):
            image_bytes = io.BytesIO()
            Image.open("TILE_SMALL.jpg").save(image_bytes, format="JPEG")
            image_bytes.seek(0)
            return StreamingResponse(image_bytes, media_type="image/jpeg")
        """

        if tile_crop.size[0] < 256 or tile_crop.size[1] < 256:
            tile_resized = Image.open(Path(__file__).parent / "RES_LOW.jpg")
        else:
            tile_resized = tile_crop.resize((256, 256), resample=Image.LANCZOS)

        image_bytes = io.BytesIO()
        tile_resized.save(image_bytes, format="JPEG")
        return image_bytes
