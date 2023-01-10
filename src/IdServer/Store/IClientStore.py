

class IClientStore:
    def __init__(self):
        pass

    def init_store(self):
        raise NotImplemented()

    def get_client_by_id(self, client_id):
        raise NotImplemented()

    def get_all_clients(self):
        raise NotImplemented()

    def add_client(self, client):
        raise NotImplemented()