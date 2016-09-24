from enum import Enum

class ChangeType(Enum):
    add = 0       # File added with unknown origin
    remove = 1    # File removed from repository
    modify = 2    # File contents modified
    move = 3      # File copied from existing path. Original path removed before commit
    copy = 4      # File copied from existing path.
    derived = 5   # File copied or moved from existing path and modified before commit

class ChangeSet:
    def __init__(self, changes, tags, identifier, author, message, timestamp):
        self.changes = changes
        self.identifier = identifier
        self.author = author
        self.message = message
        self.timestamp = timestamp

class Change:
    """ Represents a change between to revisions of an object in a repository"""
    def __init__(self, repository, previous_path, previous_revision, current_path,
                 current_revision, action):
        self.repository = repository
        self.previous_path = previous_path
        self.previous_revision = previous_revision
        self.current_path = current_path
        self.current_revision = current_revision
        self.action = action

    def __eq__(self, other):
        return ((self.repository == other.repository) and
                (self.previous_path == other.previous_path) and
                (self.previous_revision == other.previous_revision) and
                (self.current_path == other.current_path) and
                (self.current_revision == other.current_revision) and
                (self.action == other.action))

    def __repr__(self):
        return "{}: ({}) {}@{} => {}@{}".format(
            self.repository, self.action, self.previous_path,
            self.previous_revision, self.current_path, self.current_revision)


    def __str__(self):
        if (self.action == ChangeType.add):
            return "Added {name} (Current Rev: {revision})".format(
                name = self.current_path,
                revision = self.current_revision
                )
        elif (self.action == ChangeType.remove):
             return "Removed {name} (Last Rev: {revision})".format(
                name = self.previous_path,
                revision = self.previous_revision
                )
        elif (self.action == ChangeType.modify):
             return "Modified {name} ({previous} ==> {current})".format(
                name = self.current_path,
                previous = self.previous_revision,
                current = self.current_revision
                )