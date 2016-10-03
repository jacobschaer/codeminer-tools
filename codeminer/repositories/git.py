import os, tempfile, shutil
from io import StringIO

import git

from codeminer.repositories.repository import change_dir, Repository
from codeminer.repositories.change import ChangeType, Change, ChangeSet

def open_repository(path, workspace=None, **kwargs):
    cleanup=False
    if not os.path.exists(path):
        checkout_path = tempfile.mkdtemp(dir=workspace)
        client = git.Repo.clone_from(path, checkout_path, **kwargs)
        path = checkout_path
        cleanup=True
    return GitRepository(path, cleanup=cleanup)

class GitRepository(Repository):
    def __init__(self, path, cleanup=False):
        self.cleanup = cleanup
        self.path = path
        self.client = git.Repo(path)
        self.name = 'GIT'

    def __del__(self):
        if self.cleanup:
            shutil.rmtree(self.path)

    @change_dir
    def walk_history(self):
        for head in self.client.heads:
            for commit in self.client.iter_commits(head):
                author = commit.author
                message = commit.message
                date = commit.committed_date
                sha = commit.binsha
                changes = diff.stats
                for change in changs:
                    repo.git.diff(change)

    @change_dir
    def get_head_revision(self):
        return self.client.commit().binsha

    @change_dir
    def get_changeset(self, revision=None):
        commit = self.client.commit(revision)
        author = commit.author
        message = commit.message
        date = commit.committed_date
        changes = []
        parents = commit.parents
        tags = []
        identifier = commit.binsha

        # If there's no parents, then this must be the first commit
        # in the tree. In that case, all files must be "added"
        if not parents:
            for item in commit.tree.traverse():
                if item.type == 'blob':
                    changes.append(Change(self, None, None, item.path,
                        identifier, ChangeType.add))

        else:
            # Default to using the first parent
            for diff in commit.diff(parents[0]):
                action = diff.change_type
                previous_path = diff.a_path
                current_path = diff.b_path
                current_revision = identifier
                if action == git.diff.DiffIndex.change_type.A:
                    # Add
                    action = ChangeType.add
                    previous_revision = None
                    previous_path = None
                    for parent in parents:
                        if current_path in parent:
                            action = ChangeType.copy
                            previous_revision = parent.binsha
                            previous_path = current_path
                elif action == git.diff.DiffIndex.change_type.D:
                    # Delete
                    action = ChangeType.remove
                    previous_revision = parents[0].binsha
                    previous_path = previous_path
                    current_revision = None
                    current_path = None
                elif action == git.diff.DiffIndex.change_type.R:
                    # Rename - so must have been a similar file in the tree
                    if diff.a_blob == diff.b_blob:
                        action = ChangeType.move
                    else:
                        action = ChangeType.derived
                    previous_revision = parents[0].binsha
                elif action == git.diff.DiffIndex.change_type.M:
                    # Modify
                    action = ChangeType.modify
                    previous_revision = parents[0].binsha

                changes.append(Change(self, previous_path, previous_revision, current_path,
                     current_revision, action))
        return ChangeSet(changes, tags=tags, identifier=identifier, author=author, message=message, timestamp=date)

    @change_dir
    def get_file_contents(self, path, revision=None):
        pass