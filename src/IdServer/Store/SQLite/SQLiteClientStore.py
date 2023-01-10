from Store import IClientStore, IUserStore
from Models.Client import Client
from Models.User import User
import sqlite3


class SQLiteClientStore(IClientStore.IClientStore, IUserStore.IUserStore):
    def __init__(self, store_path="db.sqlite"):
        IClientStore.IClientStore.__init__(self)
        self.connect = lambda: sqlite3.connect(store_path)

    def init_store(self):
        schema = ["""
        CREATE TABLE IF NOT EXISTS `clients` (
            `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            `client_id` VARCHAR(32) NOT NULL UNIQUE,
            `client_secret` VARCHAR(255),
            `access_token_lifetime` INT NOT NULL
        );""",
                  """CREATE TABLE IF NOT EXISTS `client_scopes` (
            `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            `client_id` INT(11) NOT NULL,
            `scope` VARCHAR(32) NOT NULL
        );""",
                  """CREATE TABLE IF NOT EXISTS `client_grant_types` (
            `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            `client_id` INT(11) NOT NULL,
            `grant_type` VARCHAR(32) NOT NULL
        );""",
                  """CREATE TABLE IF NOT EXISTS `users` (
            `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            `client_id` INTEGER NOT NULL,
            `username` VARCHAR(32) NOT NULL,
            `password` VARCHAR(255) NOT NULL,
            `subject` VARCHAR(255) NOT NULL
        );""",
                  """CREATE TABLE IF NOT EXISTS `api_resources` (
            `id` INTEGER PRIMARY KEY AUTOINCREMENT,
            `client_id` INTEGER NOT NULL,
            `resource` VARCHAR(32) NOT NULL
        );"""]

        cnx = self.connect()
        cursor = cnx.cursor()

        for s in schema:
            cursor.execute(s)

        cursor.close()
        cnx.close()

        # clients = self.get_all_clients()
        # if len(clients) == 0:
        # todo provision client
        # pass

    def get_all_clients(self):
        clients = []

        cnx = self.connect()
        cursor = cnx.cursor()

        client_query = "SELECT id, client_id, client_secret, access_token_lifetime FROM clients"
        scopes_query = "SELECT client_id, scope FROM client_scopes"
        grants_query = "SELECT client_id, grant_type FROM client_grant_types"
        api_resources_query = "SELECT client_id, resource FROM api_resources"

        cursor.execute(client_query)
        db_clients = cursor.fetchall()

        cursor.execute(scopes_query)
        db_scopes = cursor.fetchall()

        cursor.execute(grants_query)
        db_grant_types = cursor.fetchall()

        cursor.execute(api_resources_query)
        db_resources = cursor.fetchall()

        clients_dict = {}

        for db_c in db_clients:
            client = Client(id=db_c[0], client_id=db_c[1], client_secret=db_c[2], access_token_lifetime=db_c[3])
            clients_dict[db_c[0]] = client
            clients.append(client)

        for db_s in db_scopes:
            if db_s[0] in clients_dict:
                clients_dict[db_s[0]].allowed_scopes.append(db_s[1])

        for db_gt in db_grant_types:
            if db_gt[0] in clients_dict:
                clients_dict[db_gt[0]].allowed_grant_types.append(db_gt[1])

        for db_res in db_resources:
            if db_res[0] in clients_dict:
                clients_dict[db_res[0]].api_resources.append(db_res[1])

        cursor.close()
        cnx.close()

        return clients

    def get_client_by_id(self, client_id):
        cnx = self.connect()
        cursor = cnx.cursor()
        client = None
        # todo fix this query plzzz
        query = """SELECT c.client_id, c.client_secret, cs.scope, gt.grant_type FROM clients c 
                JOIN client_scopes cs ON cs.client_id = c.id 
                JOIN client_grant_types gt ON gt.client_id = c.id 
                WHERE c.client_id = %s"""

        cursor.execute(query, (client_id,))

        cursor.close()
        cnx.close()
        return client

    def get_user_with_login(self, username, password, client_id):
        user = None
        cnx = self.connect()
        cursor = cnx.cursor()
        query = """SELECT id, username, password, subject FROM users
         WHERE username = ? AND password = ? AND client_id = ?"""

        cursor.execute(query, (username, password, client_id,))

        rs = cursor.fetchone()
        if rs:
            user = User(id=rs[0], username=rs[1], password=rs[2], subject=rs[3], client_id=client_id)

        cursor.close()
        cnx.close()

        return user

    def add_user(self, user):
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """SELECT id FROM users WHERE (username = ? AND client_id = ?) OR (subject = ? AND client_id = ?)"""
        cursor.execute(query, (user.username, user.client_id, user.subject, user.client_id,))

        rs = cursor.fetchone()
        if rs:
            print("User {0} already exists for client {1}".format(user.username, user.client_id))
            cursor.close()
            cnx.close()
            return None

        query = """INSERT INTO users (username, password, subject, client_id) VALUES (?, ?, ?, ?);"""

        cursor.execute(query, (user.username, user.password, user.subject, user.client_id,))

        cnx.commit()

        query = """SELECT id FROM users WHERE username = ? AND client_id = ?"""
        cursor.execute(query, (user.username, user.client_id,))

        rs = cursor.fetchone()
        user.id = rs[0]
        cursor.close()
        cnx.close()

        return rs[0]
