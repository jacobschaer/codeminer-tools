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
                if copy.previous_path == remove.previous_path:
                    copy.action = ChangeType.move
                    redundant.append(remove)
                    break

        # Filter out the redundant changes
        combined = [x for x in self.changes if x not in redundant]

        # Go through and look for 'Derived' which are copy/move + modify
        for commit in combined:
            if ((commit.action == ChangeType.move) or
                (commit.action == ChangeType.copy)):
                old_contents = commit.repository.get_object(commit.previous_path, commit.previous_revision)
                new_contents = commit.repository.get_object(commit.current_path, commit.current_revision)
                if old_contents.read() != new_contents.read():
                    commit.action = ChangeType.derived
        
        self.changes = combined


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