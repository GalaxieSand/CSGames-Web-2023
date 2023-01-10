
class IUserStore:
    def __init__(self):
        pass

    def get_user_with_login(self, username, password, client_id):
        raise NotImplemented()

    def add_user(self, user):
        raise NotImplemented()