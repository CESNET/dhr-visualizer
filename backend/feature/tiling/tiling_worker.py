import logging

import mercantile
import numpy as np

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
                Path(variables.DOCKER_SHARED_DATA_DIRECTORY) /
                self._processed_feature.get_request_hash() /
                selected_file
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

    def save_tile(self) -> Path:
        tile_bounds = mercantile.bounds((self._x, self._y, self._z))
        self._logger.debug(f"[{__name__}]: Tile bounds: {tile_bounds}")

        tile_directory = self._selected_file.parent / self._selected_file.stem / f"{self._z}/{self._x}/"
        tile_directory.mkdir(parents=True, exist_ok=True)
        tile_file = tile_directory / f"{self._y}.jpg"

        if tile_file.is_dir():
            raise TilingWorkerOutputFileIsDirectory(tile_file)

        if tile_file.is_file():
            return tile_file

        self._logger.debug(f"[{__name__}]: Will output tile into: {tile_file}")

        left, top = self._coords_to_pixel(tile_bounds.west, tile_bounds.north)
        right, bottom = self._coords_to_pixel(tile_bounds.east, tile_bounds.south)

        if left > self._image_width or top > self._image_height or right < 0 or bottom < 0:
            raise TilingWorkerTileOutOfBounds(
                request_hash=self._processed_feature.get_request_hash(),
                z=self._z, x=self._x, y=self._y
            )

        if self._should_return_lowres_tile(left, top, right, bottom):
            return self._get_lowres_tile()

        tile_crop = self._image_file.crop((int(left), int(top), int(right), int(bottom)))
        tile_resized = tile_crop.resize((256, 256), resample=Image.LANCZOS)
        tile_resized.save(tile_file, format="JPEG")

        return tile_file

    def _should_return_lowres_tile(self, left: float, top: float, right: float, bottom: float) -> bool:
        crop_width = right - left
        crop_height = bottom - top

        # Invalid crop
        if crop_width <= 0 or crop_height <= 0:
            return True

        # Low resolution
        if crop_width < 256 or crop_height < 256:
            return True

        return False

    def _get_lowres_tile(self) -> Path:
        lowres_file = Path(variables.DOCKER_SHARED_DATA_DIRECTORY) / "LOW_RES.jpg"
        
        if not lowres_file.exists():
            src = Path(__file__).parent / "LOW_RES.jpg"
            lowres_file.write_bytes(src.read_bytes())

        return lowres_file
