import json
import logging

import utils

from config import variables
from exceptions.dataspace_odata import *
from http_requestable_object import HTTPRequestableObject


class DataspaceOData(HTTPRequestableObject):
    _feature_id = None

    def __init__(
            self,
            base_url=utils.normalize_url(variables.DATASPACE_ODATA_BASE_URL),
            feature_id=None,
            logger=logging.getLogger(__name__)
    ):
        if feature_id is None:
            raise DataspaceODataFeatureIdNotProvided()
        self._feature_id = feature_id

        super().__init__(
            base_url=base_url,
            logger=logger,
        )

    def get_s3_path(self) -> str:
        endpoint = f"Products({self._feature_id})"

        try:
            response_content_dict = json.loads(self._send_request(endpoint=endpoint).content)
        except Exception as e:
            raise e

        try:
            return response_content_dict['S3Path']
        except KeyError:
            raise DataspaceODataFeatureDoesNotContainS3Path(feature_id=self._feature_id)
        except Exception as e:
            raise e
