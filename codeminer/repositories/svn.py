import datetime
import os
import shlex
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import xmltodict

from codeminer.repositories.repository import Repository
from codeminer.repositories.change import ChangeType, Change, ChangeSet

def open_repository(path, workspace=None, **kwargs):
    checkout_path = tempfile.mkdtemp(dir=workspace)
    client = SVNClient()
    if os.path.exists(path):
        # Remove the checkout path so we can use copytree() which
        # requires the path must not exist. We're only using mkdtemp()
        # to ensure the file path is safe to use
        os.rmdir(checkout_path)
        print("Copying {} to {}".format(path,checkout_path))
        shutil.copytree(path, checkout_path, symlinks=True)
    else:
        client.run_subcommand('clone', path, cwd=checkout_path)
    return SVNRepository(checkout_path, cleanup=True)

class SVNClient:
    def __init__(self, username=None, password=None, *args, **kwargs):
        self.username = username
        self.password = password

    def run_subcommand(self, subcommand, *args, flags=None, cwd=None, **kwargs):
        command = ['svn', subcommand]
        for arg in args:
            command.append(arg)

        if flags:
            for flag in flags:
                dashes = '-' if len(flag) == 1 else '--'
                command.append('{dashes}{flag}'.format(dashes=dashes, flag=flag))

        for flag, value in kwargs.items():
            dashes = '-' if len(flag) == 1 else '--'
            command.append('{dashes}{flag}'.format(dashes=dashes, flag=flag))
            command.append(value)

        print('$ {command}'.format(command=' '.join(command)))

        result = subprocess.run(command, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, cwd=cwd)

        return result.stdout, result.stderr


class SVNRepository(Repository):
    def __init__(self, path, cleanup=False):
        self.path = path
        self.client = SVNClient()
        self.cleanup = cleanup

    def __del__(self):
        if self.cleanup:
            shutil.rmtree(self.path)

    def info(self, target=None, rev=None):
        args = []
        kwargs = {}
        flags = ['xml']
        if target and revision:
            args.append('{target}@{revision}'.format(
                target = target, revision = rev))
        elif target:
            args.append(target)
        elif rev:
            kwargs['r'] = rev

        out, err = self.client.run_subcommand('info', *args, flags=flags,
                                              cwd=self.path, **kwargs)
        return xmltodict.parse(out)['info']['entry']

    def get_changes(self, rev):
        rev = int(rev)
        args = []
        kwargs = {'r' : str(rev)}
        flags = ['xml', 'v']

        out, err = self.client.run_subcommand('log', *args, flags=flags,
                                              cwd=self.path, **kwargs)
        print(out)
        tree = ET.fromstring(out)
        changes = list()
        for path in tree.find('logentry/paths'):
            action_string = path.get('action')
            copyfrom_path = path.get('copyfrom-path', None)
            # Copies are marked as 'A' by SVN but have metadata
            # that indicates otherwise
            if copyfrom_path is not None:
                action_string = 'C'

            if action_string == 'A':
                action = ChangeType.add
                current_path = path.text[1:]
                current_revision = str(rev)
                previous_path = None
                previous_revision = None
            elif action_string == 'C':
                action = ChangeType.copy
                current_path = path.text[1:]
                current_revision = str(rev)
                previous_path = path.get('copyfrom-path')[1:]
                previous_revision = path.get('copyfrom-rev')
            elif action_string == 'D':
                action = ChangeType.remove
                current_path = None
                current_revision = None
                previous_path = path.text[1:]
                previous_revision = str(rev - 1)
            elif action_string == 'M':
                action = ChangeType.modify
                current_path = path.text[1:]
                current_revision = str(rev)
                previous_path = path.text[1:]
                previous_revision = str(rev - 1)


            changes.append(Change(self, previous_path, previous_revision,
               current_path, current_revision, action))
        return changes

    def get_object(self, path, rev=None):
        if rev:
            args = ['{path}@{rev}'.format(path=path, rev=rev)]
        else:
            args = [path]
        kwargs = {}
        flags = []
        out, err = self.client.run_subcommand('cat', *args, flags=flags,
                                              cwd=self.path, **kwargs)
        return out