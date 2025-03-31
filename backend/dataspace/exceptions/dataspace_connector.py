class DataspaceConnectorError(Exception):
    def __init__(self, message="Dataspace Connector General Error!"):
        self.message = message
        super().__init__(self.message)

class DataspaceConnectorRootURLNotProvided(DataspaceConnectorError):
    def __init__(self, message="Catalog root URL must be provided!"):
        self.message = message
        super().__init__(self.message)

class DataspaceConnectorFeatureIdNotProvided(DataspaceConnectorError):
    def __init__(self, message="Feature ID must be provided!"):
        self.message = message
        super().__init__(self.message)

class DataspaceConnectorCouldNotFetchFeature(DataspaceConnectorError):
    def __init__(self, feature_id=None, status_code=None, message="Couldn't fetch feature!"):
        if feature_id is not None:
            message += f" FeatureID: {feature_id}"

        if status_code is not None:
            message += f"; HTTP status: {status_code}"