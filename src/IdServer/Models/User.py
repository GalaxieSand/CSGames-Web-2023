import uuid
from Crypto.Hash import SHA256
from base64 import encodebytes


class User:
    def __init__(self, id=0, client_id=0, username="", password="", subject="", claims={}):
        self.id = id
        self.client_id = client_id
        self.username = username
        self.password = password
        self.subject = subject
        self.claims = {}

    @staticmethod
    def NewUser(username, password, client_id):
        return User(client_id=client_id,
                    username=username,
                    password=User.HashPassword(password),
                    subject=str(uuid.uuid4()))

    @staticmethod
    def HashPassword(clear_password):
        hasher = SHA256.new()
        hasher.update(clear_password.encode('utf-8'))
        return encodebytes(hasher.digest()).decode('utf-8')