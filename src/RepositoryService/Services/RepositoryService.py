import os
import json
import subprocess
from .GitService import GitService
from CacheManager import CacheManager
from Store.MySQL.MySQLRepositoryStore import MySQLRepositoryStore

def initialize_database(settings):
    if settings["database"]["driver"] == "mysql":
        repository_store = MySQLRepositoryStore(host=settings["database"]["host"],
                                                port=settings["database"]["port"],
                                                user=settings["database"]["user"],
                                                password=settings["database"]["password"],
                                                database=settings["database"]["database"])
        repository_store.init_store()
        return repository_store

def loadSettings(path):
    if os.path.exists(path):
        fp = open(path, 'r')
        settings = json.load(fp)
        fp.close()
        return settings


class RepositoryService:
    def __init__(self, repository_store, repositories_root, redis_host, redis_port, redis_ttl):
        self.repository_store = repository_store
        self.repository_root = repositories_root
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_ttl = redis_ttl
        self.cache = CacheManager(self.redis_host, self.redis_port)

        self.git = GitService()

    def get_diff(self, repository_id, commit, commit2=None, filepath=None):
        repository = self.repository_store.get_repository(repository_id)
        if repository is None:
            return None

        repository_path = os.path.join(self.repository_root, "{0}.git".format(repository.name))
        cache_key = "diff_{0}_{1}_{2}_{3}".format(repository_id, commit, commit2, filepath)
        diffs = self.cache.get_raw(cache_key)
        if diffs is None:
            diffs = self.git.git_diff(repository_path, commit, commit2, filepath)
            self.cache.set_raw(cache_key, diffs, self.redis_ttl)
        return diffs

    def get_all_topics(self):
        topics = self.repository_store.get_all_topics()
        return {
            "topics": [*topics.keys()]
        }

    def get_authors(self, skip, limit, filter):
        return self.repository_store.get_authors(skip, limit, filter)

    def get_repositories(self, skip, limit, filter):
        resp = self.repository_store.get_repositories(skip, limit, filter)
        repositories = resp["repositories"]
        resp["repositories"] = []
        for r in repositories:
            resp["repositories"].append(r.__dict__)

        return resp

    def get_author_repositories(self, author_id, skip=0, limit=25):
        cache_key = "author_repositories_{0}_{1}_{2}".format(author_id, skip, limit)
        author_repositories = self.cache.get_json(cache_key)
        if author_repositories is None:
            author_repositories = self.repository_store.get_author_repositories(author_id, skip, limit)

            repos = []
            for r in author_repositories["repositories"]:
                repos.append(r.__dict__)

            author_repositories["repositories"] = repos
            self.cache.set_json(cache_key, author_repositories, self.redis_ttl)

        return author_repositories

    def get_repository(self, repository_id):
        repository = self.repository_store.get_repository(repository_id)
        if repository is None:
            return None

        cache_key = "git_repository_{0}".format(repository_id)
        repository_dict = self.cache.get_json(cache_key)
        if repository_dict is None:
            repository_path = os.path.join(self.repository_root, "{0}.git".format(repository.name))
            # get branches and tags
            branches  = self.git.get_branches(repository_path)
            tags = self.git.get_tags(repository_path)
            topics = self.repository_store.get_repository_topics(repository_id)
            languages = self.repository_store.get_repository_languages(repository_id)
            authors = self.repository_store.get_repository_authors(repository_id)

            repository_dict = {
                **repository.__dict__,
                "branches": branches,
                "tags": tags,
                "topics": [*topics],
                "languages": [*languages],
                "contributors": authors
            }

            self.cache.set_json(cache_key, repository_dict, self.redis_ttl)

        return repository_dict

    def get_repository_commits(self, repository_id, skip, limit, branch):
        repository = self.repository_store.get_repository(repository_id)
        if repository is None:
            return None

        cache_key = "{0}_commits_{1}_{2}_{3}".format(repository_id, skip, limit, branch)
        commits = self.cache.get_json(cache_key)
        if commits is None:
            repository_path = os.path.join(self.repository_root, "{0}.git".format(repository.name))
            commits = self.git.get_log(skip, limit, branch, repository_path)

            self.cache.set_json(cache_key, commits, self.redis_ttl)

        return {
            "commits" : commits
        }

    def get_repository_blob_commits(self, repository_id, filepath, branch):
        repository = self.repository_store.get_repository(repository_id)
        if repository is None:
            return None

        cache_key = "{0}_blob_commits_{1}_{2}".format(repository_id, branch, filepath)
        commits = self.cache.get_json(cache_key)
        if commits is None:
            repository_path = os.path.join(self.repository_root, "{0}.git".format(repository.name))
            commits = self.git.get_log_file(filepath, branch, repository_path)
            self.cache.set_json(cache_key, commits, self.redis_ttl)

        return {
            "commits" : commits
        }

    def get_repository_tree(self, repository_id, branch, path):
        repository = self.repository_store.get_repository(repository_id)
        if repository is None:
            return None

        cache_key = "{0}_tree_{1}_{2}".format(repository_id, branch, path)
        tree = self.cache.get_json(cache_key)
        if tree is None:
            repository_path = os.path.join(self.repository_root, "{0}.git".format(repository.name))
            tree = self.git.get_tree(branch, path, repository_path)

            self.cache.set_json(cache_key, tree, self.redis_ttl)

        return {"tree": tree}

    def get_repository_file(self, repository_id, filepath, branch):
        repository = self.repository_store.get_repository(repository_id)
        if repository is None:
            return None

        cache_key = "{0}_file_{1}_{2}".format(repository_id, filepath, branch)
        file = self.cache.get_raw(cache_key)
        if file is None:
            repository_path = os.path.join(self.repository_root, "{0}.git".format(repository.name))
            file = self.git.git_show(branch, filepath, repository_path)

            if file is None:
                return None

            self.cache.set_raw(cache_key, file, self.redis_ttl)

        return file