

class SnippetsService:
    def __init__(self, snippets_store):
        self.snippets_store = snippets_store

    def delete_snippet(self, snippet_id, subject):
        self.snippets_store.delete_snippet(snippet_id, subject)

    def add_snippet(self, title, content, owner, keywords=[]):
        db_keywords = self.snippets_store.get_all_keywords()

        keywords_to_insert = []

        for k in keywords:
            if k.lower() in db_keywords:
                keywords_to_insert.append(db_keywords[k.lower()])
            else:
                keyword_id = self.snippets_store.add_keyword(k.lower())
                keywords_to_insert.append(keyword_id)

        snippet_id = self.snippets_store.add_snippet(title, content, owner, keywords_to_insert)

        return {
            "id": snippet_id
        }

    def get_snippet(self, snippet_id):
        snippet = self.snippets_store.get_snippet(snippet_id)
        return snippet

    def get_snippets(self, title="", skip=0, limit=25, keywords=[], subject=None):
        keywords_id = []
        if len(keywords) > 0:
            db_keywords = self.snippets_store.get_all_keywords()
            for k in keywords:
                if k in db_keywords:
                    keywords_id.append(db_keywords[k])

        if subject is not None:
            return self.snippets_store.get_snippets_by_subject(subject, title, skip, limit, keywords_id)

        return self.snippets_store.get_snippets(title, skip, limit, keywords_id)

    def get_all_keywords(self):
        return [*self.snippets_store.get_all_keywords()]
