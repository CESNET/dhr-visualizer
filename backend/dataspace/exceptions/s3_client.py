class S3ClientError(Exception):
    def __init__(self, message="S3 Client General Error!"):
        self.message = message
        super().__init__(self.message)


class S3ClientConfigNotProvided(S3ClientError):
    def __init__(self, message="S3 configuration must be provided!"):
        super().__init__(message=message)
