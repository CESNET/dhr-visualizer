class DataspaceODataError(Exception):
    def __init__(self, message="Copernicus Dataspace OData Connector General Error!"):
        self.message = message
        super().__init__(self.message)


class DataspaceODataUnsupportedMethod(DataspaceODataError):
    def __init__(self, message="Selected HTTP method is not supported by script.", method=None):
        if method is not None:
            self.message = f"HTTP method {method} is not supported by script."
        else:
            self.message = message

        super().__init__(self.message)


class DataspaceODataRequestTimeout(DataspaceODataError):
    def __init__(self, message="Copernicus Dataspace OData Request Timeouted", retry=None, max_retries=None):
        if retry is not None:
            self.message = f"Copernicus Dataspace OData Request Timeouted after {retry} retries."

            if max_retries is not None:
                self.message = f"{self.message} Max retries: {max_retries}."
        else:
            self.message = message

        super().__init__(self.message)


class DataspaceODataFeatureIdNotProvided(DataspaceODataError):
    def __init__(self, message="Feature ID must be provided!"):
        self.message = message
        super().__init__(self.message)


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
