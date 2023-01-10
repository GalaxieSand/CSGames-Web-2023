import mysql.connector
import time
from Models import RepositorySummary

class MySQLRepositoryStore:
    def __init__(self, host="127.0.0.1", port=3306, user="", password="", database=""):
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
        fp = open('Store/MySQL/schema.sql', 'r')
        schema = fp.read()
        fp.close()

        cnx = self.connect()
        cursor = cnx.cursor()

        cursor.execute(schema)
        cursor.close()
        cnx.close()

    def get_last_repository_github_id(self):
        github_id = None
        cnx = self.connect()
        cursor = cnx.cursor()
        query = """SELECT github_id FROM repositories ORDER BY id DESC LIMIT 1"""

        cursor.execute(query)

        rs = cursor.fetchone()
        if rs:
            github_id = rs[0]

        cursor.close()
        cnx.close()

        return github_id

    def get_all_repositories(self):
        repositories = {}
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """SELECT id, name, source_url FROM repositories"""
        cursor.execute(query)

        for row in cursor:
            repositories[row[1]] = {
                "id": row[0],
                "source_url": row[2]
            }

        cursor.close()
        cnx.close()

        return repositories

    def add_repository(self, repository_name, source_url, github_id=None):
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """INSERT INTO repositories (name, source_url, status, github_id) VALUES (%s, %s, 1, %s)"""
        cursor.execute(query, (repository_name, source_url, github_id))
        cnx.commit()

        query = """SELECT id FROM repositories WHERE source_url = %s"""
        cursor.execute(query, (source_url, ))

        rs = cursor.fetchone()

        cursor.close()
        cnx.close()
        return rs[0]

    def update_repository(self, repository_id, description, license):
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """UPDATE repositories SET description = %s, license = %s WHERE id = %s"""
        cursor.execute(query, (description, license, repository_id))

        cnx.commit()
        cursor.close()
        cnx.close()

    def update_repository_sync(self, repository_id, timestamp=int(time.time())):
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """UPDATE repositories SET last_sync = %s WHERE id = %s"""
        cursor.execute(query, (timestamp, repository_id))
        cnx.commit()
        cursor.close()
        cnx.close()

    def get_pending_sync_repository(self):
        repositories = {}

        cnx = self.connect()
        cursor = cnx.cursor()


        query = """SELECT id, name, source_url FROM repositories WHERE status = 3 AND last_sync IS NULL"""
        cursor.execute(query, )


        for row in cursor:
            repositories[row[0]] = {
                "name": row[1],
                "source_url": row[2]
            }

        cursor.close()
        cnx.close()

        return repositories

    def get_repository_languages(self, repository_id):
        languages = {}
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """SELECT l.id, l.language FROM languages l
                   INNER JOIN repositories_languages rl ON rl.language_id = l.id
                   WHERE rl.repository_id = %s"""

        cursor.execute(query, (repository_id,))

        for row in cursor:
            languages[row[1]] = row[0]

        cursor.close()
        cnx.close()

        return languages

    def get_repository_topics(self, repository_id):
        topics = {}

        cnx = self.connect()
        cursor = cnx.cursor()

        query = """SELECT t.id, t.topic FROM topics t
                   INNER JOIN repositories_topics rt ON rt.topic_id = t.id
                   WHERE rt.repository_id = %s"""

        cursor.execute(query, (repository_id, ))

        for row in cursor:
            topics[row[1]] = row[0]

        cursor.close()
        cnx.close()

        return topics

    def add_topic(self, topic):
        topic_id = None
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """INSERT INTO topics (topic) VALUES (%s);"""
        cursor.execute(query, (topic, ))

        cnx.commit()

        query = """SELECT LAST_INSERT_ID();"""
        cursor.execute(query)
        rs = cursor.fetchone()
        topic_id = rs[0]

        cursor.close()
        cnx.close()

        return topic_id

    def add_language(self, language):
        language_id = None
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """INSERT INTO languages (language) VALUES (%s);"""
        cursor.execute(query, (language, ))
        cnx.commit()

        query = """SELECT LAST_INSERT_ID(); """
        cursor.execute(query)
        rs = cursor.fetchone()
        language_id = rs[0]

        cnx.commit()

        cursor.close()
        cnx.close()

        return language_id

    def get_all_topics(self):
        topics = {}
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """SELECT id, topic FROM topics"""
        cursor.execute(query)

        for row in cursor:
            topics[row[1]] = row[0]

        cursor.close()
        cnx.close()

        return topics

    def get_all_languages(self):
        languages = {}
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """SELECT id, language FROM languages"""
        cursor.execute(query)

        for row in cursor:
            languages[row[1]] = row[0]

        cursor.close()
        cnx.close()

        return languages

    def add_repository_topic(self, repository_id, topic_id):
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """INSERT INTO repositories_topics (repository_id, topic_id) VALUES (%s, %s)"""

        cursor.execute(query, (repository_id, topic_id, ))

        cnx.commit()

        cursor.close()
        cnx.close()

    def add_repository_language(self, repository_id, language_id):
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """INSERT INTO repositories_languages (repository_id, language_id) VALUES (%s, %s)"""

        cursor.execute(query, (repository_id, language_id,))

        cnx.commit()

        cursor.close()
        cnx.close()

    def get_repository(self, repository_id):
        repository = None
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """SELECT id, name, description, license FROM repositories WHERE id = %s AND status = 3"""
        cursor.execute(query, (repository_id, ))

        rs = cursor.fetchone()
        if rs:
            repository = RepositorySummary(id=rs[0], name=rs[1], description=rs[2], license=rs[3])

        return repository

    def get_authors(self, skip=0, limit=25, filter="*"):
        totalMatches = 0
        authors = []

        cnx = self.connect()
        cursor = cnx.cursor()

        if filter == "*":
            query = "SELECT COUNT(id) FROM authors"
            cursor.execute(query)
        else:
            if '%' not in filter:
                filter  = "%{0}%".format(filter)
            query = "SELECT COUNT(id) FROM authors WHERE author LIKE %s"
            cursor.execute(query, (filter, ))

        rs = cursor.fetchone()
        if rs:
            totalMatches = rs[0]

        if filter == "*":
            query = """SELECT id, author, email, subject FROM authors  LIMIT %s, %s"""
            cursor.execute(query, (skip, limit, ))
        else:
            query = """SELECT id, author, email, subject FROM authors WHERE author LIKE %s LIMIT %s, %s"""
            cursor.execute(query, (filter, skip, limit, ))

        for row in cursor:
            author = {
                "id": row[0],
                "author": row[1],
                "email": row[2],
                "subject": row[3]
            }
            authors.append(author)

        cursor.close()
        cnx.close()

        return {
            "totalMatches": totalMatches,
            "authors": authors
        }


    def get_author_repositories(self, author_id, skip=0, limit=25):
        totalMatches = 0
        repositories = []

        cnx = self.connect()
        cursor = cnx.cursor()

        query = """SELECT COUNT(r.id) FROM repositories r 
        INNER JOIN repositories_authors ra ON ra.repository_id = r.id
        WHERE ra.author_id = %s AND status = 3"""
        cursor.execute(query, (author_id, ))

        rs = cursor.fetchone()
        if rs:
            totalMatches = rs[0]


        query = """SELECT r.id, r.name, r.description, r.license FROM repositories r 
        INNER JOIN repositories_authors ra ON ra.repository_id = r.id
        WHERE ra.author_id = %s AND status = 3 LIMIT %s, %s"""
        cursor.execute(query, (author_id, skip, limit, ))



        for row in cursor:
            repository = RepositorySummary(id=row[0], name=row[1], description=row[2], license=row[3])
            repositories.append(repository)

        cursor.close()
        cnx.close()

        return {
            "totalMatches": totalMatches,
            "repositories": repositories
        }


    def get_repositories(self, skip=0, limit=25, filter="*"):
        totalMatches = 0
        repositories = []

        cnx = self.connect()
        cursor = cnx.cursor()

        if filter == "*":
            query = "SELECT COUNT(id) FROM repositories WHERE status = 3 "
            cursor.execute(query)
        else:
            if '%' not in filter:
                filter  = "%{0}%".format(filter)
            query = "SELECT COUNT(id) FROM repositories WHERE status = 3 AND name LIKE %s"
            cursor.execute(query, (filter, ))

        rs = cursor.fetchone()
        if rs:
            totalMatches = rs[0]

        if filter == "*":
            query = """SELECT id, name, description, license FROM repositories WHERE status = 3 LIMIT %s, %s"""
            cursor.execute(query, (skip, limit, ))
        else:
            query = """SELECT id, name, description, license FROM repositories WHERE name LIKE %s AND status = 3 LIMIT %s, %s"""
            cursor.execute(query, (filter, skip, limit, ))


        for row in cursor:
            repository = RepositorySummary(id=row[0], name=row[1], description=row[2], license=row[3])
            repositories.append(repository)

        cursor.close()
        cnx.close()

        return {
            "totalMatches": totalMatches,
            "repositories": repositories
        }

    def get_repository_authors(self, repository_id):
        authors = []
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """SELECT a.id, a.author, a.email, a.subject FROM authors a 
        INNER JOIN repositories_authors ra ON ra.author_id = a.id WHERE ra.repository_id = %s"""
        cursor.execute(query, (repository_id, ))

        for row in cursor:
            authors.append({
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "subject": row[3]
            })

        cursor.close()
        cnx.close()

        return authors