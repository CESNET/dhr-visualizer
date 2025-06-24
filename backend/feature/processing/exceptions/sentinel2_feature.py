class Sentinel2FeatureError(Exception):
    def __init__(self, message="Sentinel-2 Feature General Error!"):
        self.message = message
        super().__init__(self.message)


class Sentinel2FeatureCantExtractUTMZone(Sentinel2FeatureError):
    def __init__(self, message="Can't extract UTM zone from Sentinel-2 filename!", feature_id=None):
        if feature_id is not None:
            message = f"{message} feature_id: {feature_id}"
        super().__init__(message)
