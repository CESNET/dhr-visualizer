import logging
import pyproj
import re

from typing import Dict, Any

from feature.processing.processed_feature import ProcessedFeature

from feature.processing.exceptions.sentinel2_feature import *


class Sentinel2Feature(ProcessedFeature):
    _utm_zone: int = None

    def __init__(
            self, logger: logging.Logger = logging.getLogger(name=__name__),
            feature_id: str = None, platform: str = None, filters: Dict[str, Any] = None,
            request_hash: str = None
    ):
        super().__init__(
            logger=logger,
            feature_id=feature_id,
            platform=platform,
            filters=filters,
            request_hash=request_hash
        )

        self._logger.debug(f"[{__name__}]: Sentinel-2 feature initialized")

    def _filter_available_files(self, available_files: list[tuple[str, str]] = None) -> list[tuple[str, str]]:
        if available_files is None:
            return []

        filtered_files = []

        selected_bands_pattern = "|".join(self._get_selected_bands())
        extensions = ['jp2', 'j2k', 'jpf', 'jpm', 'jpg2', 'j2c', 'jpc', 'jpx', 'mj2']
        extensions_pattern = "|".join(extensions)
        regex_pattern = rf"([^/]+)/GRANULE/([^/]+)/IMG_DATA/(?:R\d{{2}}m/)?([^/]+_({selected_bands_pattern})(?:_\d{{2}}m)?\.({extensions_pattern}))"

        for available_file in available_files:
            if re.match(regex_pattern, available_file[0].strip()):
                filtered_files.append(available_file)

        return filtered_files

    def _get_selected_bands(self):
        selected_bands = []

        for band in self._filters['bands']:
            band = band.upper()
            if band == 'B8A' or band == 'TCI':
                selected_bands.append(band)
            else:
                selected_bands.append(f'B{int(band[1:]):02}')

        return selected_bands

    def _utm_to_epsg_zone(self) -> int:
        if self._utm_zone is None:
            match = re.search(r"_T(\d{2}[A-Z]{3})_", self.get_feature_name())
            if not match:
                self._logger.debug(f"[{__name__}]: _utm_to_epsg: can't extract UTM zone from feature name")
                raise Sentinel2FeatureCantExtractUTMZone(feature_id=self.get_feature_id())

            zone_number = int(match.group(1)[:3][:-1])
            zone_letter = match.group(1)[:3][-1].upper()

            if 'C' <= zone_letter <= 'M':
                self._utm_zone = 32700 + zone_number  # southern hemisphere
            else:
                self._utm_zone = 32600 + zone_number  # northern hemisphere

        return self._utm_zone

    def get_bbox_webmercator(self) -> list[float]:
        self._logger.debug(f"[{__name__}]: get_bbox_webmercator: input bbox: {self._get_bbox()}")
        min_lon, min_lat, max_lon, max_lat = self._get_bbox()

        transformer = pyproj.Transformer.from_crs(
            #crs_from=self._utm_to_epsg_zone(),
            crs_from=4326,
            crs_to=self._WEB_MERCATOR_CRS,
            always_xy=True
        )

        self._logger.debug(f"[{__name__}]: get_bbox_webmercator: transformer: {transformer}")

        min_lat, min_lon = transformer.transform(min_lon, min_lat)
        max_lat, max_lon = transformer.transform(max_lon, max_lat)

        webmercator_bbox = [min_lon, min_lat, max_lon, max_lat]

        self._logger.debug(f"[{__name__}]: get_bbox_webmercator: webmercator_bbox: {webmercator_bbox}")

        return webmercator_bbox
