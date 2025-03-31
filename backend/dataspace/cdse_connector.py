import logging

from config.variables import CDSE_CATALOG_ROOT
from dataspace.dataspace_connector import DataspaceConnector

class CDSEConnector(DataspaceConnector):
    _resto_id: str | None = None

    def __init__(self, feature_id=None, logger: logging.Logger = logging.getLogger(__name__)):
        super().__init__(root_url=CDSE_CATALOG_ROOT, feature_id=feature_id, logger=logger)