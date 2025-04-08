class HTTPClientError(Exception):
    def __init__(self, message="HTTP Client General Error!"):
        self.message = message
        super().__init__(self.message)


class HTTPClientConfigNotProvided(HTTPClientError):
    def __init__(self, message="HTTP configuration must be provided!"):
        super().__init__(message=message)
