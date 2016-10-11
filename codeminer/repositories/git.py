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
                yield self.process_commit(commit)

    @change_dir
    def get_head_revision(self):
        return self.client.commit().binsha

    @change_dir
    def get_changeset(self, revision='HEAD'):
        commit = self.client.commit(revision)
        return self.process_commit(commit)

    @change_dir
    def process_commit(self, commit):
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
            for diff in parents[0].diff(commit):
                action = diff.change_type
                previous_path = diff.a_path
                current_path = diff.b_path
                current_revision = identifier
                if action == 'A':
                    # Add
                    action = ChangeType.add
                    previous_revision = None
                    previous_path = None
                    for parent in parents:
                        for previous_blob in parent.tree.traverse():
                            if ((previous_blob.type == 'blob') and
                                (previous_blob.binsha == diff.b_blob.binsha)):
                                    action = ChangeType.copy
                                    previous_revision = parent.binsha
                                    previous_path = previous_blob.path
                                    break
                        # We're lazy... first match is good enough, break out.. useful
                        # if there's multiple parents - we only search as many as necessary
                        if previous_path is not None:
                            break
                elif action == 'D':
                    # Delete
                    action = ChangeType.remove
                    previous_revision = parents[0].binsha
                    previous_path = previous_path
                    current_revision = None
                    current_path = None
                elif action[0] == 'R':
                    # Rename - so must have been a similar file in the tree
                    # Typically these are in the form 'R100' which means 100% match
                    if ((action[1:] == '100') or (diff.a_blob == diff.b_blob)):
                        action = ChangeType.move
                    else:
                        action = ChangeType.derived
                    previous_revision = parents[0].binsha
                elif action == 'M':
                    # Modify
                    action = ChangeType.modify
                    previous_revision = parents[0].binsha
                else:
                    raise Exception("Unknown Git Action Type: %s" % action)

                changes.append(Change(self, previous_path, previous_revision, current_path,
                     current_revision, action))
        return ChangeSet(changes, tags=tags, identifier=identifier, author=author, message=message, timestamp=date)

    @change_dir
    def get_file_contents(self, path, revision=None):
        commit = self.client.commit(revision)
        for blob in commit.tree.traverse(predicate=lambda obj, depth: obj.path == path):
            return blob.data_stream
        return None