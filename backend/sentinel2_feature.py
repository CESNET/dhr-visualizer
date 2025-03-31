from requested_feature import RequestedFeature

import logging
import re

from typing import Dict, Any


class Sentinel2Feature(RequestedFeature):
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

    def _filter_available_files(self, available_files: list[tuple[str, str]] = None) -> list[tuple[str, str]]:
        if available_files is None:
            return []

        filtered_files = []

        selected_bands_pattern = "|".join(self._get_selected_bands())
        extensions = ['jp2', 'j2k', 'jpf', 'jpm', 'jpg2', 'j2c', 'jpc', 'jpx', 'mj2']
        extensions_pattern = "|".join(extensions)
        regex_patern = rf"([^/]+)/GRANULE/([^/]+)/IMG_DATA/([^/]+_({selected_bands_pattern})\.({extensions_pattern}))"

        for available_file in available_files:
            if re.match(regex_patern, available_file[0].strip()):
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
