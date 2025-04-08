class RequestedFeatureError(Exception):
    def __init__(self, message="Requested Feature General Error!"):
        self.message = message
        super().__init__(self.message)


class RequestedFeatureIDNotSpecified(RequestedFeatureError):
    def __init__(self, message="Requested Feature ID Not Specified!"):
        super().__init__(message)


class RequestedFeatureS3DownloadFailed(RequestedFeatureError):
    def __init__(
            self,
            message="Requested Feature S3 Download Failed!",
            feature_id=None
    ):
        if feature_id is None:
            self._message = message
        else:
            self._message = f"Requested Feature S3 Download Failed for {feature_id}!"

        super().__init__(self._message)
