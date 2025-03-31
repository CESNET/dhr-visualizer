import logging
from abc import abstractmethod

from dataspace.exceptions.dataspace_connector import *

from utilities.http_requestable_object import HTTPRequestableObject


class DataspaceConnector(HTTPRequestableObject):
    _feature_id: str = None

    def __init__(
            self,
            root_url=None, feature_id=None,
            logger: logging.Logger = logging.getLogger(__name__)
    ):
        if root_url is None:
            raise DataspaceConnectorRootURLNotProvided()

        if feature_id is None:
            raise DataspaceConnectorFeatureIdNotProvided()

        self._feature_id = feature_id

        super().__init__(
            root_url=root_url,
            logger=logger,
        )

        try:
            self.get_feature()
        except DataspaceConnectorCouldNotFetchFeature as e:
            raise e

    @abstractmethod
    def get_feature(self) -> dict:
        pass

    @abstractmethod
    def get_available_files(self) -> list[str]:
        pass
