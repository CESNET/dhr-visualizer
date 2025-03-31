from dataspace.exceptions.dataspace_connector import DataspaceConnectorCouldNotFetchFeature

class CDSEConnectorError(Exception):
    def __init__(self, message="CDSE Connector General Error!"):
        self.message = message
        super().__init__(self.message)

class CDSEConnectorFeatureDoesNotContainS3Path(CDSEConnectorError):
    def __init__(self, message="Feature does not contain S3Path key!", feature_id=None):
        if feature_id is not None:
            message = f"Feature ID {feature_id} does not contain S3Path key!"
        super().__init__(message)

class CDSEConnectorCouldNotFetchFeature(DataspaceConnectorCouldNotFetchFeature):
    def __init__(self, feature_id=None, status_code=None, message="Couldn't fetch feature!"):
        super().__init__(feature_id=feature_id, status_code=status_code, message=message)
