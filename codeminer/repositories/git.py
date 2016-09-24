import os, tempfile, shutil
from io import StringIO

import git

from codeminer.repositories.repository import change_dir, Repository
from codeminer.repositories.change import ChangeType, Change, ChangeSet

def create_repository(path=None, **kwargs):
    pass

def open_repository(path, workspace=None, **kwargs):
    from os.path import join
    checkout_path = tempfile.mkdtemp(dir=workspace)
    if os.path.exists(path):
        os.rmdir(checkout_path)
        print("Copying {} to {}".format(path,checkout_path))
        shutil.copytree(path, checkout_path, symlinks=True)
    else:
        client = git.Repo.clone_from(path, checkout_path, **kwargs)
    return GitRepository(checkout_path, cleanup=True)

class GitRepository(git.Repo, Repository):
    def __init__(self, path, cleanup=False):
        self.cleanup = cleanup
        self.path = path
        git.Repo.__init__(self, path)

    def __del__(self):
        if self.cleanup:
            shutil.rmtree(self.path)

    @change_dir
    def walk_history(self):
        for head in self.heads:
            for commit in self.iter_commits(head):
                author = commit.author
                message = commit.message
                date = commit.committed_date
                sha = commit.binsha
                changes = diff.stats
                for change in changs:
                    repo.git.diff(change)

    @change_dir
    def get_changes(self, rev):
        pass

    @change_dir
    def get_object(self, path, rev=None):
        pass