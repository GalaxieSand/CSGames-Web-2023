import os
from Crypto.PublicKey import RSA
from .JSONWebKey import JSONWebKey

class OpenIdConfiguration:
    PrivateKeyFilename = "cert.key"
    CertificateFilename = "cert.pem"
    DefaultLength = 2048

    def __init__(self, uri, private_key_path=None, certificate_path=None):
        self.privateKey = None
        self.certificate = None

        self.uri = uri.rstrip('/')

        self.wellKnown = PublicOpenIdConfiguration(self.uri)

        self.jsonWebKeySet = []

        self.__loadPrivateKey(private_key_path)
        self.__loadCertificate(certificate_path)
        self.__initKeySet()

    def __loadPrivateKey(self, private_key_path):
        if private_key_path is None:
            private_key_path = os.path.join(os.getcwd(), self.PrivateKeyFilename)

        if os.path.exists(private_key_path):
            print("Loading private at {0}".format(private_key_path))
            fp = open(private_key_path, 'rb')
            self.privateKey = RSA.importKey(fp.read())
            fp.close()
            return

        raise Exception("Private key not found, generate a certificate and relaunch")
        # print("Private key not found at {0}, generating a key of {1} bits".format(private_key_path, self.DefaultLength))
        # self.privateKey = RSA.generate(self.DefaultLength, Random.new().read)

        # fp = open(private_key_path, 'wb')
        # fp.write(self.privateKey.exportKey('PEM'))
        # fp.close()

    def __loadCertificate(self, certificate_path):
        if certificate_path is None:
            certificate_path = os.path.join(os.getcwd(), self.CertificateFilename)

        fp = open(certificate_path, 'rb')
        self.certificate = RSA.importKey(fp.read())
        fp.close()

    def __initKeySet(self):
        self.jsonWebKeySet.append(JSONWebKey(self.certificate))

    def __initWellKnown(self):
        pass


class PublicOpenIdConfiguration:
    def __init__(self, uri):
        self.issuer = uri
        self.jwks_uri = "{0}/.well-known/openid-configuration/jwks".format(uri)
        self.token_endpoint = "{0}/connect/token".format(uri)

        self.frontchannel_logout_supported = False
        self.frontchannel_logout_session_supported = False
        self.backchannel_logout_supported = False
        self.backchannel_logout_session_supported =  False
        self.grant_types_supported = ["client_credentials"]
        self.response_types_supported = ["token"]
        self.token_endpoint_auth_methods_supported = ["client_secret_post"]
        self.response_modes_supported = ["form_post", "query"]
        self.id_token_signing_alg_values_supported = ["RS256"]

        """{
issuer: "",
jwks_uri: "",
authorization_endpoint: "",
token_endpoint: "",
userinfo_endpoint: "",
end_session_endpoint: "",
check_session_iframe: "",
revocation_endpoint: "",
device_authorization_endpoint: "",
frontchannel_logout_supported: true,
frontchannel_logout_session_supported: true,
backchannel_logout_supported: true,
backchannel_logout_session_supported: true,
scopes_supported: [
"openid",
"profile",
"email",
"offline_access"
],
claims_supported: [
"sub",
"updated_at",
"locale",
"email_verified",
"email",
],
grant_types_supported: [
"authorization_code",
"client_credentials"
],
response_types_supported: [
"code",
"token",
"id_token",
"id_token token",
"code id_token",
"code token",
"code id_token token"
],
response_modes_supported: [
"form_post",
"query",
"fragment"
],
token_endpoint_auth_methods_supported: [
"client_secret_basic",
"client_secret_post"
],
subject_types_supported: [
"public"
],
id_token_signing_alg_values_supported: [
"RS256"
],
code_challenge_methods_supported: [
"plain",
"S256"
],
request_parameter_supported: true
}"""