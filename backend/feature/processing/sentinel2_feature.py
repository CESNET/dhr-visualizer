import logging
import re

from typing import Dict, Any

from feature.processing.processed_feature import ProcessedFeature


class Sentinel2Feature(ProcessedFeature):
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
