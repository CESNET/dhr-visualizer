import json
import logging

import utils

from config import variables
from exceptions.dhr_stac import *
from http_requestable_object import HTTPRequestableObject


class DHRSTAC(HTTPRequestableObject):
    _feature_id = None

    def __init__(
            self,
            base_url=utils.normalize_url(variables.DHR_STAC_BASE_URL),
            feature_id=None,
            logger=logging.getLogger(__name__)
    ):
        if feature_id is None:
            raise DHRSTACFeatureIdNotProvided()
        self._feature_id = feature_id

        super().__init__(
            base_url=base_url,
            logger=logger,
        )
