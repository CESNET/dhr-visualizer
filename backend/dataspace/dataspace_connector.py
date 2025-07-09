import logging

from abc import abstractmethod
from pathlib import Path

from dataspace.http_requestable_object import HTTPRequestableObject

from dataspace.exceptions.dataspace_connector import *


class DataspaceConnector(HTTPRequestableObject):
    _feature_id: str | None = None
    _feature: dict | None = None
    _workdir: Path | None = None

    def __init__(
            self,
            root_url=None, feature_id=None, workdir=None,
            logger: logging.Logger = logging.getLogger(__name__)
    ):
        if root_url is None:
            raise DataspaceConnectorRootURLNotProvided()

        if feature_id is None:
            raise DataspaceConnectorFeatureIdNotProvided()
        self._feature_id = feature_id

        if workdir is None:
            raise DataspaceConnectorWorkdirNotSpecified()
        self._workdir = Path(workdir.name)

        super().__init__(
            root_url=root_url,
            logger=logger,
        )

        try:
            self._get_feature()
        except DataspaceConnectorCouldNotFetchFeature as e:
            raise e

    @abstractmethod
    def _get_feature(self) -> dict:
        pass

    @abstractmethod
    def _get_asset_path(self, full_path: str | None = None) -> str:
        pass

    @abstractmethod
    def get_available_files(self) -> list[tuple[str, str]]:
        pass

    @abstractmethod
    def download_selected_files(self, files_to_download: list[tuple[str, str]]) -> list[str]:
        pass

    @abstractmethod
    def get_polygon(self) ->list[list[float]]:
        pass

    def get_rectangular_bbox(self) -> list[float]:
        polygon = self.get_polygon()

        lats = [pt[1] for pt in polygon]
        lons = [pt[0] for pt in polygon]

        return [min(lons), min(lats), max(lons), max(lats)]

