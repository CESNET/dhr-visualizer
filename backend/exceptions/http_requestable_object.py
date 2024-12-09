class HTTPRequestableObjectError(Exception):
    def __init__(self, message="HTTP Requestable Object General Error!"):
        self.message = message
        super().__init__(self.message)


class HTTPRequestableObjectBaseURLNotSpecified(HTTPRequestableObjectError):
    def __init__(self, message="HTTP Requestable Object Base URL Not Specified!"):
        super().__init__(message)


class HTTPRequestableObjectUnsupportedMethod(HTTPRequestableObjectError):
    def __init__(self, message="Selected HTTP method is not supported by script.", method=None):
        if method is not None:
            self.message = f"HTTP method {method} is not supported by script."
        else:
            self.message = message

        super().__init__(self.message)


class HTTPRequestableObjectRequestTimeout(HTTPRequestableObjectError):
    def __init__(self, message="Request timeouted", retry=None, max_retries=None):
        if retry is not None:
            self.message = f"Request timeouted after {retry} retries."

            if max_retries is not None:
                self.message = f"{self.message} Max retries: {max_retries}."
        else:
            self.message = message

        super().__init__(self.message)
