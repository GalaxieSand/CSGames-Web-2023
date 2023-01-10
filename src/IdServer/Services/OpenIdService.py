from Store import SQLiteClientStore
from Models import OpenIdConfiguration, OpenIdConstants
from .OpenIdException import OpenIdException
from Crypto.Hash import SHA256
from base64 import encodebytes
from .UserService import UserService
import time
import jwt
import os
import json


def loadSettings(path):
    if os.path.exists(path):
        fp = open(path, 'r')
        settings = json.load(fp)
        fp.close()
        return settings

    return {
      "database": {
        "driver": "mysql",
        "host": "127.18.0.5",
        "user": "idserver",
        "password": "dev",
        "database": "idserver"
      },
      "token": {
        "signingCertificatePath": "cert.pem",
        "privateKeyPath": "cert.key"
      }
    }


class OpenIdService:

    @staticmethod
    def HashSecret(clear_password):
        hasher = SHA256.new()
        hasher.update(clear_password.encode('utf-8'))
        return encodebytes(hasher.digest()).decode('utf-8').rstrip('\n').rstrip('=')

    def __init__(self, uri, client_store, user_store, private_key_path, certificate_path):
        self.clientStore = client_store
        self.userStore = user_store
        self.uri = uri
        self.openIdConfiguration = None
        self.clients = {}
        self.userService = None
        self.private_key_path = private_key_path
        self.certificate_path = certificate_path

    def init_service(self):
        self.openIdConfiguration = OpenIdConfiguration(self.uri, self.private_key_path, self.certificate_path)

        clients = self.clientStore.get_all_clients()
        for c in clients:
            self.clients[c.client_id] = c

        self.userService = UserService(self.userStore)

    def get_client(self, client_id):
        if client_id in self.clients:
            return self.clients[client_id]

        return None

    def create_service_account_token(self, client, requested_scopes):
        token_data = self.get_generic_token_data(client, requested_scopes)
        token_data['role'] = 'service'

        return jwt.encode(token_data,
                          self.openIdConfiguration.privateKey.exportKey('PEM'),
                          algorithm='RS256',
                          headers=self.get_token_header()).decode('utf-8')

    def create_user_token(self, client, username, password, requested_scopes):
        user = self.userService.user_login(client, username, password)
        if user is None:
            raise OpenIdException("Invalid user")

        token_data = self.get_generic_token_data(client, requested_scopes)
        token_data = {
            **token_data,
            **user.claims,
            'identity': user.username,
            'sub': user.subject,
        }

        return jwt.encode(token_data,
                          self.openIdConfiguration.privateKey.exportKey('PEM'),
                          algorithm='RS256',
                          headers=self.get_token_header()).decode('utf-8')

    def get_generic_token_data(self, client, scopes=[]):
        nbf = int(time.time())
        exp = nbf + client.access_token_lifetime

        claims = {}

        for client_claim in client.claims:
            claims[client_claim] = client.claims[client_claim]

        return {"client_id": client.client_id,
                "iss": self.openIdConfiguration.wellKnown.issuer,
                "aud": [self.openIdConfiguration.wellKnown.issuer, *client.api_resources],
                "scope": scopes,
                "nbf": nbf,
                "exp": exp,
                **claims}

    def get_token_header(self):
        return {"kid": self.openIdConfiguration.jsonWebKeySet[0].kid,
                "x5t": self.openIdConfiguration.jsonWebKeySet[0].x5t}

    def create_token(self, client_id, client_secret, grant_type, scopes=[], username=None, password=None):
        client = self.get_client(client_id)
        if client is None:
            raise OpenIdException("Invalid client")

        if client.client_secret.rstrip('=') != OpenIdService.HashSecret(client_secret).rstrip('='):
            raise OpenIdException("Invalid client")

        if grant_type not in client.allowed_grant_types:
            raise OpenIdException("Invalid client")

        for scope in scopes:
            if scope not in client.allowed_scopes:
                raise OpenIdException("Invalid scope")

        if len(scopes) == 0:
            # adding all allowed scopes for that client
            scopes = client.allowed_scopes

        token_information = {
            "access_token": "",
            "ttl": client.access_token_lifetime,
            "scopes": scopes
        }

        if username is None and password is None and grant_type == OpenIdConstants.GrantType.ClientCredentials:
            token_information['access_token'] = self.create_service_account_token(client, scopes)
            return token_information

        if username is not None and password is not None and grant_type == OpenIdConstants.GrantType.ClientCredentials:
            raise OpenIdException("Invalid grant type")

        if username is None and password is None and grant_type == OpenIdConstants.GrantType.Password:
            raise OpenIdException("Username and password are required for Password grant_type")

        token_information['access_token'] = self.create_user_token(client, username, password, scopes)

        return token_information

