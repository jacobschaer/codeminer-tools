from enum import Enum

from codeminer_tools.repositories.file import RepositoryFile


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
        # for a entity to be "moved" to multiple other entities
        redundant = []
        for copy in copies:
            for remove in removes:
                copy_previous_entity_paths = [x.path for x in copy.previous_entities]
                remove_previous_entity_paths = [x.path for x in remove.previous_entities]
                for x in copy_previous_entity_paths:
                    if x in remove_previous_entity_paths:
                        copy.action = ChangeType.move
                        redundant.append(remove)
                        break

        # Filter out the redundant changes
        combined_changes = [x for x in self.changes if x not in redundant]

        # Go through and look for 'Derived' which are copy/move + modify
        for change in combined_changes:
            if ((change.action == ChangeType.move) or
                    (change.action == ChangeType.copy)):
                if (change.previous_entities[0].read() != change.current_entity.read()):
                    change.action = ChangeType.derived

        self.changes = combined_changes


class Change:
    """ Represents a change between two revisions of an object in a repository"""

    def __init__(
            self,
            repository,
            previous_path,
            previous_revision,
            previous_type,
            current_path,
            current_revision,
            current_type,
            action):
        self.previous_entities = []
        if previous_path is not None:
            self.previous_entities.append(RepositoryFile(
                repository, previous_path, previous_revision))
        self.current_entity = RepositoryFile(
            repository, current_path, current_revision)
        self.action = action

    def add_previous_entity(
            self,
            repository,
            previous_path,
            previous_revision):
        self.previous_entities.append(RepositoryFile(
            repository, previous_path, previous_revision
            ))

    def __eq__(self, other):
        return ((self.action == other.action) and
                (self.previous_entities == other.previous_entities) and
                (self.current_entity == other.current_entity))

    def __repr__(self):
        if len(self.previous_entities) > 0:
            return "{}: {}@{} => ({}) => {}: {}@{}".format(
                self.previous_entities[0].repository.name, self.previous_entities[0].path,
                self.previous_entities[0].revision, self.action, self.current_entity.repository.name,
                self.current_entity.path, self.current_entity.revision)
        else:
            return "{}: {}@{} => ({}) => {}: {}@{}".format(
                None, None, None, self.action, self.current_entity.repository.name,
                self.current_entity.path, self.current_entity.revision)

    def __str__(self):
        if (self.action == ChangeType.add):
            return "Added {name} (Current Rev: {revision})".format(
                name=self.current_entity.path,
                revision=self.current_entity.revision
            )
        elif (self.action == ChangeType.remove):
            return "Removed {name} (Last Rev: {revision})".format(
                name=self.previous_entities[0].path,
                revision=self.previous_entities[0].revision
            )
        elif (self.action == ChangeType.modify):
            return "Modified {name} ({previous} ==> {current})".format(
                name=self.current_entity.path,
                previous=self.previous_entities[0].revision,
                current=self.current_entity.revision
            )
