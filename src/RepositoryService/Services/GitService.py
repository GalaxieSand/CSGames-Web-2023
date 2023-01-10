import subprocess
import re
import random

class GitService:
    AnonymousAuthorRegex = """([a-f0-9]{12}) <([a-f0-9]{12})@anemail.net>"""

    def __init__(self):
        pass

    def get_branches(self, repository_path):
        proc = subprocess.Popen(["git", "branch"], stdout=subprocess.PIPE, cwd=repository_path)
        branches = []
        for line in proc.stdout:
            # parsing branch
            branch = line.decode('utf-8').lstrip(" *").rstrip(" \n")
            branches.append(branch)

        return branches

    def get_tags(self, repository_path):
        proc = subprocess.Popen(["git", "tag"], stdout=subprocess.PIPE, cwd=repository_path)
        tags = []
        for line in proc.stdout:
            # parsing tag
            tag = line.decode('utf-8').lstrip(" *").rstrip(" \n")
            tags.append(tag)

        return tags

    def parse_commits_log(self, proc):
        commits = []
        commit = {}
        authors = []

        for line in proc.stdout:
            # parsing tag
            log = line.decode('utf-8').rstrip(" \n")

            if log.startswith("commit"):
                if "author" in commit and "date" in commit:
                    # packing
                    commits.append(commit)
                commit = {
                    "hash": log.replace('commit ', '')
                }
            elif log.startswith("Author"):
                author = log.replace("Author:", "").lstrip()

                if re.match(self.AnonymousAuthorRegex, author):
                    authors.append(author)
                else:
                    if len(authors) >= 1:
                        author = random.choice(authors)
                    else:
                        author = "********  ***@***"

                commit["author"] = author
            elif log.startswith("Date"):
                commit["date"] = log.replace("Date:", "").lstrip()
            elif len(log) > 0:
                # message
                if "message" in commit:
                    commit["message"] += log
                else:
                    commit["message"] = log

        if commits[-1] != commit and "author" in commit and "date" in commit:
            # pushing last commit
            commits.append(commit)

        return commits

    def get_log(self, skip, limit, branch, repository_path):
        # todo add regex validation on branch
        proc = subprocess.Popen(["git", "log", "--skip", str(skip), "-n", str(limit), branch], stdout=subprocess.PIPE, cwd=repository_path)
        return self.parse_commits_log(proc)

    def git_diff(self, repository_path, commit, commit2=None, filepath=None):
        cmds = ["git", "diff", commit]

        if commit2 is not None:
            cmds.append(commit2)

        if filepath is not None:
            cmds.append("--")
            cmds.append(filepath)

        proc = subprocess.Popen(cmds, stdout=subprocess.PIPE, cwd=repository_path)
        diffs = ""
        for line in proc.stdout:
            diffs += line.decode('utf-8')

        return diffs

    def get_log_file(self, filepath, branch, repository_path):
        proc = subprocess.Popen(["git", "log", branch, "--", "{0}".format(filepath)], stdout=subprocess.PIPE,
                                cwd=repository_path)
        return self.parse_commits_log(proc)

    def get_tree(self, branch, path, repository_path):
        # todo add regex validation on path
        proc = subprocess.Popen(["git", "ls-tree", branch, path], stdout=subprocess.PIPE, cwd=repository_path)
        entries = []
        for line in proc.stdout:
            entry = line.decode('utf-8').rstrip('\n')

            vars = entry.split('\t')
            metadata = vars[0].split(' ')
            entry_dict = {
                "tree_hash": metadata[2],
                "type": metadata[1],
                "filename": vars[1]
            }

            entries.append(entry_dict)

        return entries

    def git_show(self, branch, filepath, repository_path):
        proc = subprocess.Popen(["git", "show", "{0}:{1}".format(branch, filepath)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=repository_path)
        # todo catch fatal
        data = b""
        for line in proc.stdout:
            data += line

        stderr = proc.stderr.read().decode('utf-8')
        if 'fatal' in stderr:
            return None

        return data