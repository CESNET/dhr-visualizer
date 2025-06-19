class ProcessedFeatureError(Exception):
    def __init__(self, message="Processed Feature General Error!"):
        self.message = message
        super().__init__(self.message)


class ProcessedFeatureIDNotSpecified(ProcessedFeatureError):
    def __init__(self, message="Processed Feature ID not specified!"):
        super().__init__(message)


class ProcessedFeatureS3DownloadFailed(ProcessedFeatureError):
    def __init__(self, message="Processed Feature S3 download failed!", feature_id=None):
        if feature_id is None:
            self._message = message
        else:
            self._message = f"Processed Feature S3 download failed for {feature_id}!"

        super().__init__(self._message)


class ProcessedFeatureBboxNotSet(ProcessedFeatureError):
    def __init__(self, message="Processed Feature bbox not set!", feature_id=None):
        if feature_id is None:
            self._message = message
        else:
            self._message = f"Processed Feature bbox not set for {feature_id}!"

        super().__init__(self._message)


class ProcessedFeatureOutputDirectoryNotSet(ProcessedFeatureError):
    def __init__(self, message="Processed Feature output directory not set!", feature_id=None):
        if feature_id is None:
            self._message = message
        else:
            self._message = f"Processed Feature output directory not set for {feature_id}!"

        super().__init__(self._message)

class ProcessedFeatureBboxForSeparateFilesNotConsistent(ProcessedFeatureError):
    def __init__(self, message="bboxes for GJTIFF output files are not consistent!", feature_id=None):
        if feature_id is None:
            self._message = message
        else:
            self._message = f"bboxes for GJTIFF output files are not consistent for {feature_id}!"

        super().__init__(self._message)
