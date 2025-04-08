from dataspace.exceptions.dataspace_connector import DataspaceConnectorCouldNotFetchFeature


class DHRConnectorError(Exception):
    def __init__(self, message="DHR Connector General Error!"):
        self.message = message
        super().__init__(self.message)


class DHRConnectorTooManyFeaturesReturned(DHRConnectorError):
    def __init__(self, message="Too many features returned!", returned=None):
        self.message = message

        if returned is not None:
            self.message += f" Returned features: {returned}"

        super().__init__(self.message)


class DHRConnectorIsNotRequestedByUser(DHRConnectorError):
    def __init__(
            self,
            message="Something that should never have happened has happened! :-( "
                    "Eventhough user did not wanted to use DHR, we tried to initialize its connector."
    ):
        self.message = message
        super().__init__(self.message)


class DHRConnectorCouldNotFetchFeature(DataspaceConnectorCouldNotFetchFeature):
    def __init__(self, feature_id=None, status_code=None, message="Couldn't fetch feature!"):
        super().__init__(feature_id=feature_id, status_code=status_code, message=message)
