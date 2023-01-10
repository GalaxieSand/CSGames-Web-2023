import base64
from Crypto.PublicKey import RSA
import time


class JWTPublicKeyCacheEntry:
    def __init__(self, web_key):
        self.created = int(time.time())
        self.webKey = web_key
        self.rsaKey = RSA.importKey(base64.b64decode(web_key['x5c'][0]))
        self.pemKey = self.rsaKey.exportKey('PEM')

