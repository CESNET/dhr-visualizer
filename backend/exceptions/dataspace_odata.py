class DataspaceODataError(Exception):
    def __init__(self, message="Copernicus Dataspace OData Connector General Error!"):
        self.message = message
        super().__init__(self.message)


class DataspaceODataFeatureIdNotProvided(DataspaceODataError):
    def __init__(self, message="Feature ID must be provided!"):
        self.message = message
        super().__init__(self.message)

class DataspaceODataFeatureDoesNotContainS3Path(DataspaceODataError):
    def __init__(self, message="Feature does not contain S3Path key!", feature_id=None):
        if feature_id is not None:
            message = f"Feature ID {feature_id} does not contain S3Path key!"
        super().__init__(message)


class DataspaceODataFeatureNotFound(DataspaceODataError):
    def __init__(self, message="Feature not found in OData catalogue!", feature_id=None):
        if feature_id is not None:
            message = f"Feature ID {feature_id} not found in OData catalogue!"

        super().__init__(message)


class DataspaceODataMultipleFeaturesFound(DataspaceODataError):
    def __init__(self, message="Multiple features found in OData catalogue!", feature_id=None):
        if feature_id is not None:
            message = f"Multiple features found in OData catalogue for feature_id {feature_id}!"

        super().__init__(message)
