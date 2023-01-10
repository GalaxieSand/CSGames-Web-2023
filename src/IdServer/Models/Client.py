


class Client:
    def __init__(self,
                 id=0,
                 client_id=None,
                 client_secret=None,
                 allowed_grant_types=[],
                 allowed_scopes=[],
                 api_resources=[],
                 access_token_lifetime=3600,
                 claims={}):

        self.id = id
        self.client_id = client_id
        self.client_secret = client_secret
        self.allowed_grant_types = allowed_grant_types
        self.access_token_lifetime = access_token_lifetime
        self.allowed_scopes = allowed_scopes
        self.api_resources = api_resources
        self.claims = claims

