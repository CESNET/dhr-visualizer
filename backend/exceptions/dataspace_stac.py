class DataspaceSTACError(Exception):
    def __init__(self, message="Copernicus Dataspace STAC Connector General Error!"):
        self.message = message
        super().__init__(self.message)


class DataspaceSTACUnsupportedMethod(DataspaceSTACError):
    def __init__(self, message="Selected HTTP method is not supported by script.", method=None):
        if method is not None:
            self.message = f"HTTP method {method} is not supported by script."
        else:
            self.message = message

        super().__init__(self.message)


class DataspaceSTACRequestTimeout(DataspaceSTACError):
    def __init__(self, message="Copernicus Dataspace STAC Request Timeouted", retry=None, max_retries=None):
        if retry is not None:
            self.message = f"Copernicus Dataspace STAC Request Timeouted after {retry} retries."

            if max_retries is not None:
                self.message = f"{self.message} Max retries: {max_retries}."
        else:
            self.message = message

        super().__init__(self.message)


class DataspaceSTACFeatureIdNotProvided(DataspaceSTACError):
    def __init__(self, message="Feature ID must be provided!"):
        self.message = message
        super().__init__(self.message)


class DataspaceSTACFeatureNotFound(DataspaceSTACError):
    def __init__(self, message="Feature not found in STAC catalogue!", feature_id=None):
        if feature_id is not None:
            message = f"Feature ID {feature_id} not found in STAC catalogue!"

        super().__init__(message)


class DataspaceSTACMultipleFeaturesFound(DataspaceSTACError):
    def __init__(self, message="Multiple features found in STAC catalogue!", feature_id=None):
        if feature_id is not None:
            message = f"Multiple features found in STAC catalogue for feature_id {feature_id}!"

        super().__init__(message)
