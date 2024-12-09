class DHRSTACError(Exception):
    def __init__(self, message="DHR STAC Connector General Error!"):
        self.message = message
        super().__init__(self.message)


class DHRSTACFeatureIdNotProvided(DHRSTACError):
    def __init__(self, message="Feature ID must be provided!"):
        self.message = message
        super().__init__(self.message)
