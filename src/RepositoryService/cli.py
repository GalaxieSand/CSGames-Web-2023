#!/usr/bin/env python3
import sys
import argparse
import os
import json
from Store.MySQL.MySQLRepositoryStore import MySQLRepositoryStore
from Services.RepositoryService import RepositoryService, loadSettings, initialize_database
from urllib import request
import emoji
import re


help_str = """
Usage
cli [verb] [arg1] [arg2] ...

Verbs available


"""


def printHelp(exitCode=0):
    print(help_str)
    exit(exitCode)


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


class AutoImportRepositories(CliAction):
    RepositoriesUrl = "https://api.github.com/repositories?since={0}"

    def __init__(self, repository_store, token):
        CliAction.__init__(self)
        self.repository = repository_store
        self.token = token

    def run(self):
        if len(self.args) == 0:
            print("Error: Missing limit arguments")
            printHelp(-1)

        existing_repositories = self.repository.get_all_repositories()
        last_github_id = self.repository.get_last_repository_github_id()
        limit = int(self.args[0])

        if last_github_id is None:
            last_github_id = 0

        req = request.Request(self.RepositoriesUrl.format(last_github_id), headers={
            "Authorization": "token {0}".format(self.token)
        })

        resp = request.urlopen(req)
        repositories = json.load(resp)
        repository_imported = 0
        continue_import = True

        while continue_import:
            for repository in repositories:
                try:
                    full_name = repository["full_name"]
                    local_name = full_name.split('/')[-1]

                    if local_name not in existing_repositories:
                        # adding repository
                        repository_imported += 1
                        github_id = int(repository["id"])
                        url = "https://github.com/{0}.git".format(full_name)

                        self.repository.add_repository(local_name, url, github_id)
                        last_github_id = github_id

                        print("Auto-importing {0} as {1}".format(url, local_name))

                        existing_repositories[local_name] = {
                            "source_url": url
                        }

                    if repository_imported >= limit:
                        print("{0} repositories was imported, quitting...".format(limit))
                        exit(0)
                except Exception as err:
                    print("error whith [0], skipping".format(local_name))
                    print(err)

            req = request.Request(self.RepositoriesUrl.format(last_github_id), headers={
                "Authorization": "token {0}".format(self.token)
            })

            resp = request.urlopen(req)
            repositories = json.load(resp)






class SyncRepositories(CliAction):
    LanguagesUri = "https://api.github.com/repos/{0}/languages"
    TopicsUri = "https://api.github.com/repos/{0}/topics"
    RepositoryUri = "https://api.github.com/repos/{0}"

    def __init__(self, repository_store, token):
        CliAction.__init__(self, with_argument=False)
        self.token = token
        self.repository = repository_store

    def run(self):
        repositories = self.repository.get_pending_sync_repository()
        languages = self.repository.get_all_languages()
        topics = self.repository.get_all_topics()

        for repository in repositories:
            print("Syncing repository {0}".format(repository))
            try:
                existing_topics = self.repository.get_repository_topics(repository)
                existing_languages = self.repository.get_repository_languages(repository)

                source_url = repositories[repository]["source_url"]
                sections = source_url.split('/')

                github_repos = "{0}/{1}".format(sections[-2], sections[-1].replace('.git', ''))
                req = request.Request(self.LanguagesUri.format(github_repos), headers={"Authorization": "token {0}".format(self.token)})
                resp = request.urlopen(req)
                repo_languages = json.load(resp)

                req = request.Request(self.TopicsUri.format(github_repos), headers={"Accept": "application/vnd.github.mercy-preview+json", "Authorization": "token {0}".format(self.token)})
                resp = request.urlopen(req)
                repo_topics = json.load(resp)["names"]

                for language in repo_languages:
                    if language in existing_languages:
                        continue

                    if language not in languages:
                        # adding in database
                        language_id = self.repository.add_language(language)
                        languages[language] = language_id

                    self.repository.add_repository_language(repository, languages[language])

                for topic in repo_topics:
                    if topic in existing_topics:
                        continue

                    if topic not in topics:
                        # adding in database
                        topic_id = self.repository.add_topic(topic)
                        topics[topic] = topic_id

                    self.repository.add_repository_topic(repository, topics[topic])

                # topics and language synced
                req = request.Request(self.RepositoryUri.format(github_repos), headers={"Authorization": "token {0}".format(self.token)})
                resp = request.urlopen(req)

                repo_json = json.load(resp)

                license = repo_json["license"]
                description = repo_json["description"]

                if license is not None:
                    license = license["name"]
                try:
                    description = re.sub(emoji.get_emoji_regexp(), r"", description)
                except TypeError:
                    description = ""

                self.repository.update_repository(repository, description, license)
                self.repository.update_repository_sync(repository)
                print("Sync of {0} completed".format(github_repos))
            except Exception as err:
                print("Sync has failed {0}".format(github_repos))
                print(err)

class InitStore(CliAction):
    def __init__(self, repository_store):
        CliAction.__init__(self, with_argument=False)
        self.repository = repository_store

    def run(self):
        self.repository.init_store()


if __name__ == "__main__":
    settings = loadSettings("setting.json")
    repository_store = initialize_database(settings)

    # parsing verbs
    print(sys.argv[0])

    if len(sys.argv) < 2:
        print("Need at least a verb")
        printHelp(-1)

    actions = {
        "sync": SyncRepositories(repository_store, settings["github_token"]),
        "init-store": InitStore(repository_store),
        "auto-import": AutoImportRepositories(repository_store, settings["github_token"])
    }

    verb = sys.argv[1]

    if verb in actions:
        actions[verb].parse_args()
        actions[verb].run()
    else:
        print("Invalid verb")
        printHelp(-1)