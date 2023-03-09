

class SecurityDefinition:
    def __init__(self, scheme="", definition={}):
        self.scheme = scheme
        self.definition = definition

    @staticmethod
    def BearerAuthorizationHeader():
        return SecurityDefinition("Bearer", {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    })
