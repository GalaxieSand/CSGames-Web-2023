#!/usr/bin/env python3
import sys
from HelperFunctions import initialize_database
from Services.OpenIdService import loadSettings
import argparse
import os
import json
from Models.Client import Client
from Services.OpenIdService import OpenIdService

help_str = """
Usage
cli [verb] [arg1] [arg2] ...

Verbs available

list-clients - return all clients in database, no arguments
import-clients-json - required filepath to JSON file
init-store - Initialize Database and creating schema
"""

class CliAction:
    def __init__(self, with_argument=True):
        self.parser = argparse.ArgumentParser()
        self.args = None
        self.with_argument = with_argument

    def parse_args(self):
        if not self.with_argument:
            return

        self.args = sys.argv[2:]

    def run(self):
        pass

class InitStoreAction(CliAction):
    def __init__(self, clientStore):
        CliAction.__init__(self, with_argument=False)
        self.clientStore = clientStore

    def run(self):
        self.clientStore.init_store()

class ListClientsAction(CliAction):
    def __init__(self, clientStore):
        CliAction.__init__(self, with_argument=False)
        self.clientStore = clientStore

    def run(self):
        clients = clientStore.get_all_clients()
        for c in clients:
            print(c.__dict__)

class ImportClientsFromJSONAction(CliAction):
    def __init__(self, clientStore):
        CliAction.__init__(self)
        self.clientStore = clientStore

    def run(self):
        clients = []
        if len(self.args) < 1:
            print("Filepath required")
            printHelp(-1)

        filepath = self.args[0]
        if not os.path.exists(filepath):
            print("File {0} doesn't exists".format(filepath))
            exit(-1)

        fp = open(filepath, 'r')
        clients_json = json.load(fp)
        fp.close()

        if "clients" not in clients_json:
            print("Invalid JSON structure")

        for client in clients_json["clients"]:
            c = Client(**client)
            c.client_secret = OpenIdService.HashSecret(c.client_secret)
            clients.append(c)

        for c in clients:
            print("Importing Client : {0}".format(c.client_id))
            self.clientStore.add_client(c)

def printHelp(exitCode=0):
    print(help_str)
    exit(exitCode)

if __name__ == "__main__":
    settings = loadSettings("setting.json")
    clientStore = initialize_database(settings)

    # parsing verbs
    print(sys.argv[0])

    if len(sys.argv) < 2:
        print("Need at least a verb")
        printHelp(-1)

    actions = {
        "list-clients": ListClientsAction(clientStore),
        "import-clients-json": ImportClientsFromJSONAction(clientStore),
        "init-store": InitStoreAction(clientStore)
    }

    verb = sys.argv[1]

    if verb in actions:
        actions[verb].parse_args()
        actions[verb].run()
    else:
        print("Invalid verb")
        printHelp(-1)