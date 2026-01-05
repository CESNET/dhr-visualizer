import hashlib
import json

from pydantic import BaseModel
from typing import Dict, Any


class ProcessedFeatureModel(BaseModel):
    feature_id: str = None
    platform: str = None
    filters: Dict[str, Any] = None
