import hashlib
import json

from pydantic import BaseModel
from typing import Dict, Any


class RequestedFeatureModel(BaseModel):
    feature_id: str = None
    platform: str = None
    filters: Dict[str, Any] = None

    def hash_myself(self) -> str:
        model_dict = self.model_dump(by_alias=True, exclude_none=True)
        model_json = json.dumps(model_dict, sort_keys=True)
        return hashlib.sha256(model_json.encode()).hexdigest()
