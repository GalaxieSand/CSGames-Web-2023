import mysql.connector
import time


class SnippetsStore:

    def __init__(self, host="127.0.0.1", port=3306, user="root", password="", database="snippets"):
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
        fp = open("Store/MySQL/schema.sql", 'r')
        schema = fp.read()
        fp.close()

        cnx = self.connect()
        cursor = cnx.cursor()

        cursor.execute(schema)

        cursor.close()
        cnx.close()

    def add_keyword(self, keyword):
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """INSERT INTO keywords (keyword) VALUES (%s)"""

        cursor.execute(query, (keyword.lower(), ))

        cnx.commit()

        query = """SELECT LAST_INSERT_ID();"""
        cursor.execute(query)
        rs = cursor.fetchone()
        keyword_id = rs[0]

        cursor.close()
        cnx.close()

        return keyword_id

    def get_all_keywords(self):
        keywords = {}
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """SELECT id, keyword FROM keywords"""

        cursor.execute(query)

        for row in cursor:
            keywords[row[1].lower()] = row[0]

        cursor.close()
        cnx.close()

        return keywords

    def get_snippets(self, title="", skip=0, limit=25, keywords_id=[]):
        results = {
            "totalMatches": 0,
            "snippets": []
        }

        cnx = self.connect()
        cursor = cnx.cursor()

        query_args = []

        query = """SELECT {0} FROM snippets s """

        if len(keywords_id) > 0:
            query += """ JOIN snippets_keywords sk ON sk.snippet_id = s.id """

            if "WHERE" not in query:
                query += "WHERE "
            else:
                query += " AND "

            kids = ""
            for kid in keywords_id:
                kids += "{0},".format(kid)

            kids = kids.rstrip(',')

            query += " sk.keyword_id IN ({0})".format(kids)

        if len(title) > 0:
            if "WHERE" in query:
                query += " AND s.title LIKE %s "
            else:
                query += " WHERE s.title LIKE %s "

            query_args.append("%{0}%".format(title))

        count_query = query.format("COUNT(s.id)")

        cursor.execute(count_query, (*query_args, ))
        rs = cursor.fetchone()
        results["totalMatches"] = rs[0]

        query += " ORDER BY created DESC LIMIT %s, %s"
        query_args.append(skip)
        query_args.append(limit)

        snippet_query = query.format("s.id, s.title, s.created, s.owner")
        cursor.execute(snippet_query, (*query_args, ))

        for row in cursor:
            results["snippets"].append({
                "id": row[0],
                "title": row[1],
                "created": row[2],
                "owner": row[3]
            })

        cursor.close()
        cnx.close()

        return results

    def get_snippets_by_subject(self, subject, title="", skip=0, limit=25, keywords_id=[]):
        results = {
            "totalMatches": 0,
            "snippets": []
        }

        cnx = self.connect()
        cursor = cnx.cursor()

        query_args = [subject]

        query = """SELECT {0} FROM snippets s """

        if len(keywords_id) > 0:
            query += """ JOIN snippets_keywords sk ON sk.snippet_id = s.id WHERE owner = %s """
            query += " AND sk.keyword_id IN ({0})".format(keywords_id.join(', '.join(str(i) for i in keywords_id)))
            for i in keywords_id:
                keywords_id.append(i)
        else:
            query += """ WHERE owner = %s """

        if len(title) > 0:
            query += " AND s.title LIKE %s "
            query_args.append("%{0}%".format(title))

        if len(keywords_id) > 0:
            query += " AND sk.keyword_id IN ({0})".format(keywords_id.join(', '.join(str(i) for i in keywords_id)))
            for i in keywords_id:
                keywords_id.append(i)

        count_query = query.format("COUNT(s.id)")

        cursor.execute(count_query, (*query_args, ))
        rs = cursor.fetchone()
        results["totalMatches"] = rs[0]

        query += " LIMIT %s, %s"
        query_args.append(skip)
        query_args.append(limit)

        snippet_query = query.format("s.id, s.title, s.created, s.owner")
        cursor.execute(snippet_query, (*query_args, ))

        for row in cursor:
            results["snippets"].append({
                "id": row[0],
                "title": row[1],
                "created": row[2],
                "owner": row[3]
            })

        cursor.close()
        cnx.close()

        return results

    def add_snippet(self, title, content, owner, keywords_id=[]):
        created = int(time.time())
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """INSERT INTO snippets (title, content, owner, created) VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, (title, content, owner, created, ))
        cnx.commit()

        query = """SELECT LAST_INSERT_ID();"""
        cursor.execute(query)
        rs = cursor.fetchone()
        snippet_id = rs[0]

        query = """INSERT INTO snippets_keywords (snippet_id, keyword_id) VALUES (%s, %s)"""
        for k_id in keywords_id:
            cursor.execute(query, (snippet_id, k_id, ))

        cnx.commit()

        cursor.close()
        cnx.close()

        return snippet_id

    def get_snippet(self, snippet_id):
        snippet = None
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """SELECT id, title, content, owner, created FROM snippets WHERE id = %s"""

        cursor.execute(query, (snippet_id, ))

        if cursor:
            rs = cursor.fetchone()

            snippet = {
                "id": rs[0],
                "title": rs[1],
                "content": rs[2],
                "created": rs[4],
                "keywords": []
            }

        if snippet is None:
            return snippet

        query = """SELECT k.keyword FROM keywords k JOIN snippets_keywords sk ON sk.keyword_id = k.id WHERE sk.snippet_id = %s"""
        cursor.execute(query, (snippet_id, ))

        for row in cursor:
            snippet["keywords"].append(row[0])

        cursor.close()
        cnx.close()

        return snippet

    def delete_snippet(self, snippet_id, subject):
        cnx = self.connect()
        cursor = cnx.cursor()

        query = """DELETE FROM snippets WHERE id = %s AND subject = %s"""

        cursor.execute(query, (snippet_id, subject, ))

        cursor.close()
        cnx.commit()
        cnx.close()
