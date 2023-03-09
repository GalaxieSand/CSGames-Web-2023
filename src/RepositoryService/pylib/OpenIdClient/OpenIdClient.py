from flask import request, g
from functools import wraps
import urllib
import jwt
import time
import json
from .JWTPublicKeyCacheEntry import JWTPublicKeyCacheEntry
from .OpenIdClientException import OpenIdClientException
from RestAPI import HTTP


class JWTCacheEntry:
    def __init__(self, jwt_header, token, jwk):
        self.jwt_header = jwt_header
        self.token = token
        self.jwk = jwk
        self.created = int(time.time())

class ClaimValidator:
    def __init__(self, claim_name):
        self.claim_name = claim_name

    def is_valid(self, claim_value):
        return True

class ClaimValueValidator(ClaimValidator):
    def __init__(self, claim_name, claim_value):
        ClaimValidator.__init__(self, claim_name)
        self.claim_value = claim_value

    def is_valid(self, claim_value):
        return self.claim_value.lower() == claim_value.lower()

class AuthorizationPolicy:
    def __init__(self):
        pass

    def is_authorized(self, decoded_token):
        raise NotImplemented

class RequiredClaimsPolicy(AuthorizationPolicy):
    def __init__(self, claims_validators=[]):
        AuthorizationPolicy.__init__(self)
        self.claims_validators = claims_validators

    def is_authorized(self, decoded_token):
        for cv in self.claims_validators:
            if cv.claim_name in decoded_token:
                if not cv.is_valid(decoded_token[cv.claim_name]):
                    return False
            else:
                return False

        return True

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
        self.policies = {}

    def get_user_token(self, issuer, client_id, client_secret, username, password, scopes=[]):
        if issuer not in self.accepted_issuers:
            raise OpenIdClientException("Issuer {0} not in accepted issuer".format(issuer))

        request_body = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "password",
            "username": username,
            "password": password
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
            'Content-Type': HTTP.MimeType.UrlFormEncoded
        }, method="POST")

        token_request.data = urllib.parse.urlencode(request_body).encode('utf-8')

        resp = urllib.request.urlopen(token_request)

        token_data = json.load(resp)

        return token_data

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
            'Content-Type': HTTP.MimeType.UrlFormEncoded
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

    def get_jwt_public_key(self, issuer, kid):

        cache_key = "{0}/{1}".format(issuer, kid)

        if cache_key in self.pubkey_cache:
            if self.pubkey_cache[cache_key].created + self.CacheLength > int(time.time()):
                return self.pubkey_cache[cache_key].pemKey

        well_known = self.get_well_known(issuer)
        jwks_uri = well_known['jwks_uri']
        req = urllib.request.urlopen(jwks_uri)
        data = req.read()

        jwks = json.loads(data.decode('utf-8'))

        for k in jwks['keys']:
            if k['kid'] == kid:
                if cache_key not in self.pubkey_cache:
                    self.pubkey_cache[cache_key] = JWTPublicKeyCacheEntry(k)
                else:
                    self.pubkey_cache[cache_key].created = int(time.time())

                return self.pubkey_cache[cache_key].pemKey

        raise Exception('Kid not found')

    def jwt_required(self, f):
        @wraps(f)
        def wrap(*args, **kwargs):

            if 'authorization' not in request.headers:
                return 'Unauthorized', 401

            bearer = request.headers['authorization'].replace('Bearer ', '')
            if bearer in self.trusted_jwt:
                jwt_cache = self.trusted_jwt[bearer]
                if jwt_cache.created + 300 > int(time.time()):
                    if jwt_cache.token['exp'] >= (time.time()):
                        g.jwt = jwt_cache.token
                        return f(*args, **kwargs)
                    else:
                        return 'Unauthorized', 401
                else:
                    del self.trusted_jwt[bearer]

            try:
                decoded_token = jwt.decode(bearer, verify=False)
                jwt_header = jwt.get_unverified_header(bearer)
                if int(decoded_token['exp']) < int(time.time()):
                    return 'Unauthorized', 401

                # accepted issuer check
                issuer = decoded_token['iss']
                if len(self.accepted_issuers) > 0:
                    if issuer not in self.accepted_issuers:
                        return 'Unauthorized', 401

                # get public key
                jwk = self.get_jwt_public_key(issuer, jwt_header['kid'])
                # real token verification with public key and audience
                decoded_token = jwt.decode(bearer, jwk, audience=self.audience)

                # scope verification
                if len(self.required_scopes) > 0:
                    for scope in self.required_scopes:
                        if scope not in decoded_token['scope']:
                            return 'Unauthorized', 401

                # claims verification

                if bearer not in self.trusted_jwt:
                    self.trusted_jwt[bearer] = JWTCacheEntry(jwt_header, decoded_token, jwk)
                else:
                    self.trusted_jwt[bearer].created = int(time.time())

                g.jwt = decoded_token

            except Exception as e:
                print(e)
                return 'Unauthorized', 401
            return f(*args, **kwargs)
        return wrap
