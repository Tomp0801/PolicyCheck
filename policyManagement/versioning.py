from git import Repo

class Versioning:
    def __init__(self, path):
        self.path = path
        self.repo = Repo(path)

    