from Crypto.Hash import SHA1
from base64 import encodebytes, b64encode, urlsafe_b64encode
import json

class JSONWebKey:
    def __init__(self, public_key):
        self.alg = "RS256"
        self.kty = "RSA"
        self.use = "sig"
        self.x5c = []
        self.n = b64encode(public_key.n.to_bytes(256, 'big')).decode('utf-8')
        self.e = b64encode(public_key.e.to_bytes(4, 'big')).decode('utf-8')
        hasher = SHA1.new()
        hasher.update(public_key.exportKey('DER'))

        fingerprint = urlsafe_b64encode(hasher.digest()).decode('utf-8')

        self.kid = fingerprint
        self.x5t = fingerprint

        self.x5c.append(b64encode(public_key.exportKey('DER')).decode('utf-8'))

    def to_json(self):
        return {
            "alg": self.alg,
            "kty": self.kty,
            "use": self.use,
            "n": self.n,
            "e": self.e,
            "kid": self.kid,
            "x5c": self.x5c,
            "x5t": self.x5t
        }