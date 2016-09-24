import os, tempfile, shutil
from io import StringIO

import hglib
from hglib.util import b

from codeminer.repositories.repository import Repository
from codeminer.repositories.change import ChangeType, Change, ChangeSet

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

    def __del__(self):
        if self.cleanup:
            shutil.rmtree(self.path)

    @change_dir
    def walk_history(self):
        for record in self.client.log(follow=True):
            rev = record.rev.decode()
            node = record.node.decode()
            tags = record.tags.decode()
            branch = record.branch.decode()
            author = record.author.decode()
            desc = record.desc.decode()
            date = record.date
            changes = self.get_changes(rev)
            yield ChangeSet(changes, tags, rev, author, desc, date)

    @change_dir
    def get_changes(self, rev):
        if not rev:
            raise Exception("Revision Number Required")

        rev = str(rev)
        parent_rev = None

        parents = self.client.parents(rev=rev.encode())
        if parents:
            parent_rev = parents[0].rev.decode()

        status = self.client.status(change=rev.encode(), copies=True)

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
                previous_path = path
                previous_revision = parent_rev
                current_revision = rev
                current_path = current_path.decode()
            elif action == 'M':
                action = ChangeType.modify
                current_path = path
                current_revision = rev
                previous_path = path
                previous_revision = parent_rev
            elif action == 'A':
                action = ChangeType.add
                current_path = path
                current_revision = rev
                previous_path = None
                previous_revision = None                
            elif action == 'R':
                action = ChangeType.remove
                current_path = None
                current_revision = None
                previous_path = path
                previous_revision = rev                   

            change = Change(
                self,              # Repository
                previous_path,     # Previous Path
                previous_revision, # Previous Revision
                current_path,      # Current Path
                current_revision,  # Current Revision
                action             # Action
            )
            if (change.action == ChangeType.copy):
                copies.append(change)
            else:
                changes.append(change)

        # Go through and find 'Moves' which are copies + removes
        removes = list()
        for copy in copies:
            for change in changes:
                if ((change.action == ChangeType.remove) and
                    (copy.previous_path == change.previous_path)):
                    copy.action = ChangeType.move
                    removes.append(change)
                    break

        combined = [change for change in changes + copies if change not in removes]

        # Go through and look for 'Derived' which are copy/move + modify
        for commit in combined:
            if ((commit.action == ChangeType.move) or
                (commit.action == ChangeType.copy)):
                old_contents = self.get_object(commit.previous_path, commit.previous_revision)
                new_contents = self.get_object(commit.current_path, commit.current_revision)
                if old_contents.read() != new_contents.read():
                    commit.action = ChangeType.derived
        return combined

    @change_dir
    def get_object(self, path, rev=None):
        from hglib.util import b, cmdbuilder
        if path is not None:
            path = b(str(path))
        if rev is not None:
            rev = b(str(rev))

        files = [path]

        args = cmdbuilder(b('cat'), r=rev, o=None, cwd=self.path, hidden=self.client.hidden, *files)
        print("hg " + ' '.join([x.decode() for x in args]))
        return StringIO(self.client.rawcommand(args).decode())