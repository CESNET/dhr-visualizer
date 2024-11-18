from requested_feature import RequestedFeature

import logging
import re

from typing import Dict, Any


class Sentinel1Feature(RequestedFeature):
    _filters_polarisation_channels_availability = None  # Todo stav tohohle po S3 filtrování nějak vracet frontendu, na frontendu pak vypsat alert

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

        self._filters_polarisation_channels_availability = {
            'VV': False,
            'VH': False,
            'HH': False,
            'HV': False
        }

    def _prepare_channel_filter_array(self) -> list:
        polarisation_filter = []
        for channels_combine in self._filters['polarisation_channels_combined']:
            channels = channels_combine.split('+')
            polarisation_filter = polarisation_filter + channels

        for channel_separate in self._filters['polarisation_channels']:
            if channel_separate not in polarisation_filter:
                polarisation_filter.append(channel_separate)

        polarisation_filter = [channel.lower() for channel in polarisation_filter]
        return polarisation_filter

    def _filter_available_s3_files(self, available_files=None):
        if available_files is None:
            available_files = []

        polarisation_filter = self._prepare_channel_filter_array()

        filtered_files = []

        for available_file in available_files:
            if (
                    re.search('/preview/', available_file)
                    or re.search('.+-report-.+\.pdf', available_file)
            ):
                continue

            if (
                    re.search('/support/', available_file)
                    or re.search('manifest.safe', available_file)
            ):
                filtered_files.append(available_file)

            for polarisation_channel in polarisation_filter:
                if re.search(f'.+-{polarisation_channel}-.+', available_file):
                    filtered_files.append(available_file)
                    self._filters_polarisation_channels_availability[polarisation_channel.upper()] = True

        return filtered_files
