import hashlib
import json

from pydantic import BaseModel
from typing import Dict, Any, List


class ProcessedFeatureModel(BaseModel):
    feature_id: str = None
    platform: str = None
    filters: Dict[str, Any] = None
    products: List[str] = None
