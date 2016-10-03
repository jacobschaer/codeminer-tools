class RepositoryFile:
    def __init__(self, repository, path, revision, tags = None):
        self.repository = repository
        self.path = path
        self.revision = revision
        self.tags = tags

    def read(self):
        return self.repository.get_file_contents(self.path, revision=self.revision).read()

    def __eq__(self, other):
        return ((self.repository == other.repository) and
                 (self.path == other.path) and
                 (self.revision == other.revision))

    def __repr__(self):
        return "<{type} : {path}@{rev}>".format(type = self.repository.name,
            path = self.path, rev = self.revision)

    def __str__(self):
        return __repr__(self)