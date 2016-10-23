from enum import Enum

from codeminer.repositories.file import RepositoryFile


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

    def optimize(self):
        removes = []
        copies = []
        adds = []

        for change in self.changes:
            if change.action == ChangeType.add:
                adds.append(change)
            elif change.action == ChangeType.copy:
                copies.append(change)
            elif change.action == ChangeType.remove:
                removes.append(change)

        # Look for copies that are really "moves"
        # Note, somewhat confusingly this logic allows the possibility
        # for a file to be "moved" to multiple other files
        redundant = []
        for copy in copies:
            for remove in removes:
                if copy.previous_file.path == remove.previous_file.path:
                    copy.action = ChangeType.move
                    redundant.append(remove)
                    break

        # Filter out the redundant changes
        combined_changes = [x for x in self.changes if x not in redundant]

        # Go through and look for 'Derived' which are copy/move + modify
        for change in combined_changes:
            if ((change.action == ChangeType.move) or
                    (change.action == ChangeType.copy)):
                if (change.previous_file.read() != change.current_file.read()):
                    change.action = ChangeType.derived

        self.changes = combined_changes


class Change:
    """ Represents a change between to revisions of an object in a repository"""

    def __init__(
            self,
            repository,
            previous_path,
            previous_revision,
            current_path,
            current_revision,
            action):
        self.previous_file = RepositoryFile(
            repository, previous_path, previous_revision)
        self.current_file = RepositoryFile(
            repository, current_path, current_revision)
        self.action = action

    def __eq__(self, other):
        return ((self.action == other.action) and
                (self.previous_file == other.previous_file) and
                (self.current_file == other.current_file))

    def __repr__(self):
        return "{}: {}@{} => ({}) => {}: {}@{}".format(
            self.previous_file.repository.name, self.previous_file.path,
            self.previous_file.revision, self.action, self.current_file.repository.name,
            self.current_file.path, self.current_file.revision)

    def __str__(self):
        if (self.action == ChangeType.add):
            return "Added {name} (Current Rev: {revision})".format(
                name=self.current_file.path,
                revision=self.current_file.revision
            )
        elif (self.action == ChangeType.remove):
            return "Removed {name} (Last Rev: {revision})".format(
                name=self.previous_file.path,
                revision=self.previous_file.revision
            )
        elif (self.action == ChangeType.modify):
            return "Modified {name} ({previous} ==> {current})".format(
                name=self.current_file.path,
                previous=self.previous_file.revision,
                current=self.current_file.revision
            )
