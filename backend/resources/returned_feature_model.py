from fastapi import HTTPException
from pydantic import BaseModel
from typing import Any

from resources.enums import RequestStatuses


class ReturnedFeatureModel(BaseModel):
    request_hash: str = None
    feature_id: str = None
    status: str | RequestStatuses = None
    hrefs: list[str] = None

    def __init__(
            self, /,
            request_hash: str = None, feature_id: str = None, status: str | RequestStatuses = None,
            hrefs: list[str] = None,
            **data: Any
    ):
        super().__init__(**data)

        if request_hash is None:
            raise HTTPException(status_code=500, detail="Request hash not provided!")
        self.request_hash = request_hash

        if feature_id is None:
            raise HTTPException(status_code=500, detail="feature_id expected in database but not found!")
        self.feature_id = feature_id

        if status is None:
            raise HTTPException(status_code=500, detail="status unknown!")
        self.status = status

        self.hrefs = hrefs
