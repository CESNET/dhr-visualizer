import logging
import re

from typing import Dict, Any

from feature.processing.processed_feature import ProcessedFeature


class Sentinel1Feature(ProcessedFeature):
    _filters_polarisation_channels_availability = None  # Todo stav tohohle po S3 filtrování nějak vracet frontendu, na frontendu pak vypsat alert

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

        self._filters_polarisation_channels_availability = {
            'VV': False,
            'HH': False,
            'VH': False,
            'HV': False,
        }

        self._logger.debug(f"[{__name__}]: Sentinel-1 feature initialized")

    def _filter_available_files(self, available_files: list[tuple[str, str]] = None) -> list[tuple[str, str]]:
        # TODO asi bude potřeba přidělat stažení i nějakých metadat pro zobrazení v mapě

        if available_files is None:
            available_files = []

        polarisation_filter = []
        for p in self._filters['polarisation_channels']:
            if '&' in p:
                polarisation_filter.extend(p.split('&'))
            else:
                polarisation_filter.append(p)
        polarisation_filter = list(set(polarisation_filter))

        filtered_files = []

        for available_file in available_files:
            if not (
                    re.search('/measurement/', available_file[0].strip())
            ):
                continue

            for polarisation_channel in polarisation_filter:
                if re.search(f'.+-{polarisation_channel.lower()}-.+', available_file[0].strip()):
                    if available_file[0].split('.')[-1].lower() in ['tif', 'tiff']:
                        self._filters_polarisation_channels_availability[polarisation_channel.upper()] = True
                        filtered_files.append(available_file)
                        break

        return filtered_files
