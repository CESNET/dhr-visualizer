from enum import Enum


class RequestStatuses(Enum):
    NON_EXISTING = "non_existing"
    ACCEPTED = "accepted"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DatabaseEntries(Enum):
    FEATURE_ID = "feature_id"
    STATUS = "status"
    PATH_TO_IMAGE = "path_to_image"
    HREF = "href"


class Platforms(Enum):
    SENTINEL_1 = "SENTINEL-1"
    SENTINEL_2 = "SENTINEL-2"
