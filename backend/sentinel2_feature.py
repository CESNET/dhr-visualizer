from requested_feature import RequestedFeature

import logging
import re

from typing import Dict, Any


class Sentinel2Feature(RequestedFeature):
    _all_bands = [
        'B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B09', 'B10', 'B11', 'B12'
    ]

    def __init__(
            self, logger: logging.Logger = logging.getLogger(name=__name__),
            feature_id: str = None, platform: str = None, filters: Dict[str, Any] = None
    ):
        super().__init__(
            logger=logger,
            feature_id=feature_id,
            platform=platform,
            filters=filters
        )

    def _filter_available_s3_files(self, available_files=None):
        if available_files is None:
            available_files = []

        excluded_bands = self._get_filter_unwanted_bands()

        filtered_files = []

        for available_file in available_files:
            if not (
                    re.search('/IMG_DATA/', available_file)
            ):
                continue

            match = re.search(r'_(B0[1-9]|B1[0-2]|B8A)([._])', available_file)
            if match:
                if match.group()[1:-1] in excluded_bands:
                    continue

            if available_file.split('.')[-1].lower() in [
                'jp2', 'j2k', 'jpf', 'jpm', 'jpg2', 'j2c', 'jpc', 'jpx', 'mj2'
            ]:
                filtered_files.append(available_file)

        return filtered_files

    def _get_filter_unwanted_bands(self):
        band_filter = []

        for band in self._filters['bands']:
            band = band.upper()
            if band == 'B8A':
                band_filter.append(band)
            else:
                band_filter.append(f'B{int(band[1:]):02}')

        unwanted_bands = list(set(self._all_bands) - set(band_filter))

        return unwanted_bands
