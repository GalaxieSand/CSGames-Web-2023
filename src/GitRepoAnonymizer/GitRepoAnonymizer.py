import subprocess
import hashlib
import random
import os
import json
import mysql.connector
from OpenIdClient import OpenIdClient
from urllib import request, parse

class Repository:
    (Pending, InProgress, Completed) = (1, 2, 3)

    def __init__(self, name, repository_url, id=0, status=Pending):
        self.repository_url = repository_url
        self.id = id
        self.status = status
        self.name = name


class AuthorMigrated:
    def __init__(self, old_email, old_author, new_email, new_author, sub, id=0):
        self.old_email = old_email
        self.old_author = old_author
        self.new_email = new_email
        self.new_author = new_author
        self.id = id
        self.sub = sub


class DbConnector:
    def __init__(self, remote_addr, user, password, db, port=3306):
        self.remote_addr = remote_addr
        self.user = user
        self.password = password
        self.db = db
        self.port = port

    def open(self):
        return mysql.connector.connect(host=self.remote_addr, user=self.user, password=self.password, database=self.db)

    def get_authors_dict(self, cnx):
        authors = {}

        query = """SELECT id, original_email, original_author, email, author, subject FROM authors"""

        cursor = cnx.cursor()
        cursor.execute(query)

        for (author_id, old_email, old_author, new_email, new_author, sub) in cursor:
            authors[old_email] = AuthorMigrated(id=author_id, old_email=old_email, old_author=old_author, new_email=new_email, new_author=new_author, sub=sub)

        cursor.close()
        return authors

    def add_author(self, cnx, author):
        query = """INSERT INTO authors (original_email, original_author, email, author, subject) VALUES (%s, %s, %s, %s, %s)"""
        cursor = cnx.cursor()

        cursor.execute(query, (author.old_email, author.old_author, author.new_email, author.new_author, author.sub, ))

        cnx.commit()

        query = """SELECT id FROM authors WHERE original_email = %s"""

        cursor.execute(query, (author.old_email, ))
        for author_id in cursor:
            author.id = author_id[0]

        cursor.close()

        return  author

    def get_pending_repositories(self, cnx, limit=1):
        repositories = []
        query = """SELECT id, name, source_url, status FROM repositories WHERE status = %s LIMIT %s"""

        cursor = cnx.cursor()
        cursor.execute(query, (Repository.Pending, limit, ))

        for (repo_id, name, source_url, status) in cursor:
            repositories.append(Repository(
                repository_url=source_url,
                status=status,
                id=repo_id,
                name=name
            ))

        cursor.close()
        return repositories

    def update_repository_status(self, cnx, repository):
        query = """UPDATE repositories SET status = %s WHERE id = %s"""

        cursor = cnx.cursor()
        cursor.execute(query, (repository.status, repository.id, ))

        cnx.commit()
        cursor.close()
        
    def link_author_to_repository(self, cnx, repository_id, author_id):
        query = """INSERT INTO repositories_authors (repository_id, author_id, write_access) VALUES (%s, %s, 1)"""
        cursor = cnx.cursor()
        cursor.execute(query, (repository_id, author_id, ))

        cnx.commit()
        cursor.close()

WORK_DIR = "work_dir"

def get_token(openidclient, authentication_setting):
    return openidclient.get_service_token(authentication_setting["issuer"], authentication_setting["client_id"], authentication_setting["client_secret"])

if __name__ == '__main__':
    fp = open('setting.json', 'r')
    setting = json.load(fp)
    fp.close()

    authentication_setting = setting["authentication"]
    openidclient = OpenIdClient(audience="gitimport", accepted_issuers=[authentication_setting["issuer"]])

    db = DbConnector(remote_addr=setting["database"]["host"],
                     user=setting["database"]["user"],
                     password=setting["database"]["password"],
                     db=setting["database"]["dbname"])
    cnx = db.open()

    while True:
        try:
            pending_repositories = db.get_pending_repositories(cnx)
            if len(pending_repositories) == 0:
                print("No more repositories to import... quitting")
                exit(0)

            repository = pending_repositories[0]
            repository.status = Repository.InProgress
            print("Starting to import {0}...".format(repository.repository_url))
            db.update_repository_status(cnx, repository)

            work_dir_path = os.path.join(os.getcwd(), WORK_DIR)
            if not os.path.exists(work_dir_path):
                # creating folder
                print("Creating Work dir, not existing ({0})".format(work_dir_path))
                os.mkdir(work_dir_path)

            proc_env = os.environ.copy()
            git_path = "git"
            filter_branch_path = proc_env["FILTER_BRANCH_PATH"]
            if "GIT_PATH" in proc_env:
                git_path = os.path.join(proc_env['GIT_PATH'], 'git')

            # cloning bare repo
            proc = subprocess.Popen([git_path, "clone", "--bare", repository.repository_url, "{0}.git".format(repository.name) ], bufsize=1, stdout=subprocess.PIPE, cwd=work_dir_path,
                                    env=proc_env)

            for l in proc.stdout:
                print(l)

            git_repo_path = os.path.join(work_dir_path, "{0}.git".format(repository.name))

            db_author_dict = db.get_authors_dict(cnx)
            author_dict = {}
            author_to_map = {}
            # listing all authors
            proc = subprocess.Popen([git_path, "log", "--all", "--format='%aN:%ae'"], stdout=subprocess.PIPE, cwd=git_repo_path, env=proc_env)

            for line in proc.stdout:
                data = line.decode('utf-8')

                data = data.rstrip('\n')
                data = data.split(':')

                author_name = data[0].rstrip("'").lstrip("'")
                author_email = data[1].rstrip("'").lstrip("'").lower()
                # must created a new author entry
                if author_email not in db_author_dict:
                    if author_email not in author_to_map:
                        author_to_map[author_email] = author_name
                elif author_email not in author_dict:
                    author_dict[author_email] = db_author_dict[author_email]

            prng = random.Random()

            print("Generating some random id for each authors")
            token = None
            for k in author_to_map:
                # generate a new name
                n = prng.randint(0, 1000000000000)
                hasher = hashlib.sha256()

                hasher.update(n.to_bytes(32, 'big'))
                hash = hasher.hexdigest()
                user_id = hash[0:12]

                # must create user
                if token is None:
                    token = get_token(openidclient, authentication_setting)
                    print("Token fecth from id server")

                req = request.Request("{0}/user/create".format(authentication_setting["issuer"]), method="POST", data=parse.urlencode({
                    "username": user_id,
                    "password": setting["default_password"]
                }).encode('utf-8'), headers={"Authorization": "Bearer {0}".format(token["access_token"]), "Content-Type": "application/x-www-form-urlencoded"})

                resp = request.urlopen(req)
                data = json.load(resp)

                author = AuthorMigrated(old_email=k, old_author=author_to_map[k], new_email="{0}@anemail.net".format(user_id), new_author=user_id, sub=data["sub"])
                author = db.add_author(cnx, author)

                db_author_dict[k] = author
                author_dict[k] = author
            token = None
            print("Generating bash script with all author changes")
            script_tpl_fp = open("{0}.tpl".format(filter_branch_path), 'r')
            script_tpl = script_tpl_fp.read()
            script_tpl_fp.close()

            bash_script = ""
            for k in author_dict:
                author_info = author_dict[k]
                bash_script += """
            if [ "${GIT_COMMITTER_EMAIL}" = "{0}"  ] || [ "${GIT_AUTHOR_EMAIL}" = "{0}" ]; then 
                export GIT_COMMITTER_NAME="{2}"
                export GIT_COMMITTER_EMAIL="{1}"
                export GIT_AUTHOR_NAME="{2}"
                export GIT_AUTHOR_EMAIL="{1}"
            fi""".format(k, author_info.new_email, author_info.new_author, GIT_COMMITTER_EMAIL="{GIT_COMMITTER_EMAIL}",
                             GIT_AUTHOR_EMAIL="{GIT_AUTHOR_EMAIL}")

            fp = open(filter_branch_path, 'w')
            fp.write(script_tpl.replace('__FILTER_ENV__', bash_script))
            fp.close()

            print("Rewriting repository history to anonymize authors")
            proc = subprocess.Popen([git_path, "filter-branch", "-f", "--tag-name-filter", "cat", "--", "--all", "--tags"],
                                    stdout=subprocess.PIPE,
                                    bufsize=1,
                                    cwd=git_repo_path,
                                    env=proc_env,
                                    universal_newlines=True)

            for l in proc.stdout:
                print(l)

            # repository done, updating progress
            repository.status = Repository.Completed
            db.update_repository_status(cnx, repository)


            for k in author_dict:
                db.link_author_to_repository(cnx, repository.id, author_dict[k].id)
        except Exception as err:
            print("Error with repository {0}".format(repository.name))
            print(err)



