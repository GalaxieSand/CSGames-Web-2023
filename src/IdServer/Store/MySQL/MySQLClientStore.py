from Store import IClientStore
from Models.Client import Client
from Models.User import User
import mysql.connector


class MySQLClientStore(IClientStore.IClientStore):
    def __init__(self, host="127.0.0.1", port=3306, user="", password="", database=""):
        IClientStore.IClientStore.__init__(self)
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        return mysql.connector.connect(host=self.host,
                                       port=self.port,
                                       user=self.user,
                                       password=self.password,
                                       database=self.database)

    def init_store(self):
        schema = """
        CREATE TABLE IF NOT EXISTS `clients` (
            `id` INT(11) NOT NULL AUTO_INCREMENT,
            `client_id` VARCHAR(32) NOT NULL UNIQUE,
            `client_secret` VARCHAR(255),
            `access_token_lifetime` INT(11) NOT NULL,
            PRIMARY KEY(`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        
        CREATE TABLE IF NOT EXISTS `client_scopes` (
            `id` INT(11) NOT NULL AUTO_INCREMENT,
            `client_id` INT(11) NOT NULL,
            `scope` VARCHAR(32) NOT NULL,
            PRIMARY KEY(`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        
        CREATE TABLE IF NOT EXISTS `client_grant_types` (
            `id` INT(11) NOT NULL AUTO_INCREMENT,
            `client_id` INT(11) NOT NULL,
            `grant_type` VARCHAR(32) NOT NULL,
            PRIMARY KEY(`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        
        CREATE TABLE IF NOT EXISTS `users` (
            `id` INT(11) NOT NULL AUTO_INCREMENT,
            `client_id` INT(11) NULL,
            `username` VARCHAR(32) NOT NULL,
            `password` VARCHAR(255) NOT NULL,
            `subject` VARCHAR(255) NOT NULL,
            PRIMARY KEY(`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        
        CREATE TABLE IF NOT EXISTS `api_resources` (
            `id` INT(11) AUTO_INCREMENT,
            `client_id` INT(11) NOT NULL,
            `resource` VARCHAR(32) NOT NULL,
            PRIMARY KEY(`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        
        CREATE TABLE IF NOT EXISTS `client_claims` (
            `id` INT(11) AUTO_INCREMENT,
            `client_id` INT(11) NOT NULL,
            `claim_name` VARCHAR(32) NOT NULL,
            `claim_value` VARCHAR(120) NOT NULL,
            PRIMARY KEY(`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        
        CREATE TABLE IF NOT EXISTS `client_claims` (
            `id` INT(11) AUTO_INCREMENT,
            `client_id` INT(11) NOT NULL,
            `claim_name` VARCHAR(32) NOT NULL,
            `claim_value` VARCHAR(120) NOT NULL,
            PRIMARY KEY(`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        
        CREATE TABLE IF NOT EXISTS `user_claims` (
            `id` INT(11) AUTO_INCREMENT,
            `user_id` INT(11) NOT NULL,
            `claim_name` VARCHAR(32) NOT NULL,
            `claim_value` VARCHAR(120) NOT NULL,
            PRIMARY KEY(`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """

        cnx = self.connect()
        cursor = cnx.cursor()

        cursor.execute(schema)

        cursor.close()
        cnx.close()

    def get_all_clients(self):
        clients = []

        cnx = self.connect()
        cursor = cnx.cursor()

        client_query = "SELECT id, client_id, client_secret, access_token_lifetime FROM clients"
        scopes_query = "SELECT client_id, scope FROM client_scopes"
        grants_query = "SELECT client_id, grant_type FROM client_grant_types"
        api_resources_query = "SELECT client_id, resource FROM api_resources"
        client_claims_query = "SELECT client_id, claim_name, claim_value FROM client_claims"

        cursor.execute(client_query)
        db_clients = cursor.fetchall()

        cursor.execute(scopes_query)
        db_scopes = cursor.fetchall()

        cursor.execute(grants_query)
        db_grant_types = cursor.fetchall()

        cursor.execute(api_resources_query)
        db_resources = cursor.fetchall()

        cursor.execute(client_claims_query)
        db_claims = cursor.fetchall()

        allowed_scopes = {}
        api_resources = {}
        grant_types = {}
        claims = {}

        for db_s in db_scopes:
            if db_s[0] not in allowed_scopes:
                allowed_scopes[db_s[0]] = []

            allowed_scopes[db_s[0]].append(db_s[1])

        for db_gt in db_grant_types:
            if db_gt[0] not in grant_types:
                grant_types[db_gt[0]] = []

            grant_types[db_gt[0]].append(db_gt[1])

        for db_res in db_resources:
            if db_res[0] not in api_resources:
                api_resources[db_res[0]] = []

            api_resources[db_res[0]].append(db_res[1])

        for db_claim in db_claims:
            if db_claim[0] not in claims:
                claims[db_claim[0]] = {}

            claims[db_claim[0]][db_claim[1]] = db_claim[2]

        for db_c in db_clients:
            client_claims = []
            if db_c[0] in claims:
                client_claims = claims[db_c[0]]

            client = Client(id=db_c[0], client_id=db_c[1], client_secret=db_c[2], access_token_lifetime=db_c[3],
                            allowed_scopes=allowed_scopes[db_c[0]], allowed_grant_types=grant_types[db_c[0]],
                            api_resources=api_resources[db_c[0]], claims=client_claims)
            clients.append(client)

        cursor.close()
        cnx.close()

        return clients

    def get_client_by_id(self, client_id):
        cnx = self.connect()
        cursor = cnx.cursor()
        client = None

        query = """SELECT c.client_id, c.client_secret, cs.scope, gt.grant_type FROM clients c 
                 JOIN client_scopes cs ON cs.client_id = c.id 
                 JOIN client_grant_types gt ON gt.client_id = c.id 
                 WHERE c.client_id = %s"""

        cursor.execute(query, (client_id,))

        cnx.commit()
        cursor.close()
        cnx.close()

        return client

    def get_user_with_login(self, username, password, client_id):
        user = None
        cnx = self.connect()
        cursor = cnx.cursor()
        query = """SELECT id, username, password, subject FROM users
          WHERE username = %s AND password = %s AND (client_id = %s OR client_id IS NULL)"""

        cursor.execute(query, (username, password, client_id,))

        rs = cursor.fetchone()
        if rs:
            user = User(id=rs[0], username=rs[1], password=rs[2], subject=rs[3], client_id=client_id)

            user.claims = {}
            query = """SELECT claim_name, claim_value FROM user_claims WHERE user_id = %s"""

            cursor.execute(query, (user.id, ))
            for row in cursor:
                user.claims[row[0]] = row[1]

        cursor.close()
        cnx.close()

        return user

    def add_client(self, client):
        cnx = self.connect()
        cursor = cnx.cursor()
        query = """SELECT id FROM clients WHERE client_id = %s"""
        cursor.execute(query, (client.client_id,))

        rs = cursor.fetchone()
        if rs:
            print("Client Id {0} already exists".format(client.client_id))
            cursor.close()
            cnx.close()
            return None

        query = """INSERT INTO clients (client_id, client_secret, access_token_lifetime) VALUES (%s, %s, %s)"""
        cursor.execute(query, (client.client_id, client.client_secret, client.access_token_lifetime, ))

        cnx.commit()

        query = """SELECT id FROM clients WHERE client_id = %s"""
        cursor.execute(query, (client.client_id,))

        rs = cursor.fetchone()
        if rs:
            client.id = rs[0]

        # adding scopes, grant type and api resource

        for scope in client.allowed_scopes:
            query = """INSERT INTO client_scopes (client_id, scope) VALUES (%s, %s)"""
            cursor.execute(query, (client.id, scope))

        for grant_type in client.allowed_grant_types:
            query = """INSERT INTO client_grant_types (client_id, grant_type) VALUES (%s, %s)"""
            cursor.execute(query, (client.id, grant_type))

        for api_resource in client.api_resources:
            query = """INSERT INTO api_resources (client_id, resource) VALUES (%s, %s)"""
            cursor.execute(query, (client.id, api_resource))

        for claim in client.claims:
            query = """INSERT INTO client_claims (client_id, claim_name, claim_value) VALUES (%s, %s, %s)"""
            cursor.execute(query, (client.id, claim, client.claims[claim],))

        cnx.commit()
        cursor.close()
        cnx.close()

    def add_user_without_client(self, user):
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """SELECT id FROM users WHERE (username = %s) OR (subject = %s)"""
        cursor.execute(query, (user.username, user.subject,))

        rs = cursor.fetchone()
        if rs:
            print("User {0} already exists for client {1}".format(user.username, user.client_id))
            cursor.close()
            cnx.close()
            return None

        query = """INSERT INTO users (username, password, subject, client_id) VALUES (%s, %s, %s, %s)"""

        cursor.execute(query, (user.username, user.password, user.subject, user.client_id,))

        cnx.commit()

        query = """SELECT id FROM users WHERE username = %s AND subject = %s"""
        cursor.execute(query, (user.username, user.subject,))

        rs = cursor.fetchone()
        user.id = rs[0]
        cursor.close()

        self.add_user_claims(user, cnx)

        cnx.close()

        return user.subject

    def add_user(self, user):
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """SELECT id FROM users WHERE (username = %s AND client_id = %s) OR (subject = %s AND client_id = %s)"""
        cursor.execute(query, (user.username, user.client_id, user.subject, user.client_id,))

        rs = cursor.fetchone()
        if rs:
            print("User {0} already exists for client {1}".format(user.username, user.client_id))
            cursor.close()
            cnx.close()
            return None

        query = """INSERT INTO users (username, password, subject, client_id) VALUES (%s, %s, %s, %s);"""

        cursor.execute(query, (user.username, user.password, user.subject, user.client_id,))

        cnx.commit()

        query = """SELECT id FROM users WHERE username = %s AND client_id = %s"""
        cursor.execute(query, (user.username, user.client_id,))

        rs = cursor.fetchone()
        user.id = rs[0]
        cursor.close()

        self.add_user_claims(user, cnx)

        cnx.close()

        return user.subject


    def add_user_claims(self, user, cnx):
        cursor = cnx.cursor()

        query = """INSERT INTO user_claims (user_id, claim_name, claim_value) VALUES (%s, %s, %s)"""

        for claim in user.claims:
            cursor.execute(query, (user.id, claim, user.claims[claim]))

        cnx.commit()
        cursor.close()
