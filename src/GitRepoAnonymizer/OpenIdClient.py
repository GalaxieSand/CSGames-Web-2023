import urllib
import json


class OpenIdClientException(Exception):
    def __init__(self, message, details=None):
        Exception.__init__(self, message)
        self.message = message
        self.details = details


class OpenIdClient:
    class WellKnownConstant:
        (Token, JsonWebKeySet, UserInfo) = ("token_endpoint", "jwks_uri", "userinfo_endpoint")

    WellKnownUri = "{0}/.well-known/openid-configuration"
    CacheLength = 900

    def __init__(self, audience, accepted_issuers=[], required_scopes=[]):
        self.accepted_issuers = accepted_issuers
        self.audience = audience
        self.pubkey_cache = {}
        self.required_scopes = required_scopes
        self.trusted_jwt = {}
        self.well_known_cache = {}

    def get_service_token(self, issuer, client_id, client_secret, scopes=[]):
        if issuer not in self.accepted_issuers:
            raise OpenIdClientException("Issuer {0} not in accepted issuer".format(issuer))

        request_body = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        }

        if len(scopes) > 0:
            scope_str = ""
            for s in scopes:
                scope_str = "{0} {1}".format(scope_str, s)

            request_body["scope"] = scope_str

        well_known = self.get_well_known(issuer)
        if self.WellKnownConstant.Token not in well_known:
            raise OpenIdClientException("Token Endpoint not found in Well Known for Issuer: {0}".format(issuer))

        token_endpoint = self.get_well_known(issuer)[self.WellKnownConstant.Token]

        token_request = urllib.request.Request(token_endpoint, headers={
            'Content-Type': "application/x-www-form-urlencoded"
        }, method="POST")

        token_request.data = urllib.parse.urlencode(request_body).encode('utf-8')

        resp = urllib.request.urlopen(token_request)

        token_data = json.load(resp)

        return token_data


    def get_well_known(self, issuer):
        if issuer in self.well_known_cache:
            return self.well_known_cache[issuer]

        issuer = issuer.rstrip('/')
        well_known_uri = self.WellKnownUri.format(issuer)
        req = urllib.request.urlopen(well_known_uri)
        data = req.read()

        well_known = json.loads(data.decode('utf-8'))
        self.well_known_cache[issuer] = well_known
        return well_known