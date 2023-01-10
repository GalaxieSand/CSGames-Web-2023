

class OpenIdClientException(Exception):
    def __init__(self, message, details=None):
        Exception.__init__(self, message)
        self.message = message
        self.details = details
