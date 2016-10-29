import os
import tempfile
import shutil
from io import BytesIO

import hglib
from hglib.util import b

from codeminer_tools.repositories.repository import Repository
from codeminer_tools.repositories.change import ChangeType, Change, ChangeSet


def change_dir(function):
    def wrap_inner(*args, **kwargs):
        self = args[0]
        old_path = os.getcwd()
        os.chdir(self.path)
        result = function(*args, **kwargs)
        os.chdir(old_path)
        return result
    return wrap_inner


def create_repository(path=None, **kwargs):
    return HgRepository(hglib.init(dest=path, **kwargs), cleanup=False)


def open_repository(path, workspace=None, **kwargs):
    checkout_path = tempfile.mkdtemp(dir=workspace)
    client = hglib.clone(source=path, dest=checkout_path, **kwargs)
    client.open()
    return HgRepository(client, cleanup=True)


class HgRepository(Repository):

    def __init__(self, client, cleanup=False):
        self.client = client
        self.cleanup = cleanup
        self.path = client.root().decode()
        self.name = 'Hg'

    def __del__(self):
        if self.cleanup:
            shutil.rmtree(self.path)

    @change_dir
    def walk_history(self):
        for record in self.client.log(follow=True):
            revision = record.rev.decode()
            node = record.node.decode()
            tags = record.tags.decode()
            branch = record.branch.decode()
            author = record.author.decode()
            desc = record.desc.decode()
            date = record.date
            changes = self.get_status(revision=revision)
            yield ChangeSet(changes, tags, revision, author, desc, date)

    @change_dir
    def get_changeset(self, revision=None):
        parent_revision = None

        if revision is None:
            log = self.client.log(revisionrange=b"tip")
        else:
            revision = str(revision)
            log = self.client.log(revrange=revision.encode())

        revision = log[0].rev.decode()
        node = log[0].node.decode()
        tags = log[0].tags.decode()
        branch = log[0].branch.decode()
        author = log[0].author.decode()
        desc = log[0].desc.decode()
        date = log[0].date
        changes = self.get_status(revision=revision)

        return ChangeSet(changes, tags, revision, author, desc, date)

    @change_dir
    def get_status(self, revision=None):
        parent_revision = None
        if revision is not None:
            status = self.client.status(change=revision.encode(), copies=True)
            parents = self.client.parents(rev=revision.encode())
        else:
            status = self.client.status(copies=True)
            parents = self.client.parents(rev=b"tip")

        if parents:
            parent_revision = parents[0].rev.decode()

        changes = list()
        copies = list()

        while len(status) > 0:
            action, path = status.pop()
            action = action.decode()
            path = path.decode()
            # The source of a copy is indicated with a ' ' status
            if action == ' ':
                _, current_path = status.pop()
                action = ChangeType.copy
                previsionious_path = path
                previsionious_revision = parent_revision
                current_revision = revision
                current_path = current_path.decode()
            elif action == 'M':
                action = ChangeType.modify
                current_path = path
                current_revision = revision
                previsionious_path = path
                previsionious_revision = parent_revision
            elif action == 'A':
                action = ChangeType.add
                current_path = path
                current_revision = revision
                previsionious_path = None
                previsionious_revision = None
            elif action == 'R':
                action = ChangeType.remove
                current_path = None
                current_revision = None
                previsionious_path = path
                previsionious_revision = revision

            change = Change(
                self,              # Repository
                previsionious_path,     # Previsionious Path
                previsionious_revision,  # Previsionious Revision
                current_path,      # Current Path
                current_revision,  # Current Revision
                action             # Action
            )
            changes.append(change)
        return changes

    @change_dir
    def get_file_contents(self, path, revision=None):
        # Note: Should ideally use the library's "cat" function, but it
        # has a bug in that it doesn't provide a "cwd" argument. This implementation
        # is based on the library's with the fix implemented.
        from hglib.util import b, cmdbuilder
        if path is not None:
            path = b(str(path))
        if revision is not None:
            revision = b(str(revision))

        files = [path]

        args = cmdbuilder(
            b('cat'),
            r=revision,
            o=None,
            cwd=self.path,
            hidden=self.client.hidden,
            *files)
        print("hg " + ' '.join([x.decode() for x in args]))
        return BytesIO(self.client.rawcommand(args))
