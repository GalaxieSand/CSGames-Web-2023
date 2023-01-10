from Store.SQLite.SQLiteClientStore import SQLiteClientStore
from Store.MySQL.MySQLClientStore import MySQLClientStore


def initialize_database(settings):
    if settings["database"]["driver"] == "mysql":
        clientStore = MySQLClientStore(settings["database"]["host"],
                                       settings["database"]["port"],
                                       settings["database"]["user"],
                                       settings["database"]["password"],
                                       settings["database"]["database"])
        return clientStore

    elif settings["database"]["driver"] == "sqlite":
        clientStore = SQLiteClientStore()

        return clientStore