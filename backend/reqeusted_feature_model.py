from pydantic import BaseModel
from typing import Dict, Any

class RequestedFeatureModel(BaseModel):
    feature_id: str = None
    platform: str = None
    filters: Dict[str, Any] = None