from enum import Enum

class EntityType(Enum):
    file = 0
    directory = 1

class RepositoryEntity:
    def __init__(self, repository, path, revision, tags=None):
        self.repository = repository
        self.path = path
        self.revision = revision
        self.tags = tags

    def __eq__(self, other):
        return ((self.repository == other.repository) and
                (self.path == other.path) and
                (self.revision == other.revision))

    def __repr__(self):
        return "<{type} : {path}@{rev}>".format(
            type=self.repository.name, path=self.path, rev=self.revision)

    def __str__(self):
        return __repr__(self)
