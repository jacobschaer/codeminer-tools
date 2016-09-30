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
from codeminer.repositories.commandlineclient import CommandLineClient

def open_repository(path, workspace=None, **kwargs):
    if os.path.exists(path):
        return SVNRepository(path)
    else:
        basename = os.path.basename(path)
        revision = None
        if '@' in basename:
            basename, revision = basename.split('@')
        checkout_path = tempfile.mkdtemp(dir=workspace)
        client = CommandLineClient('svn')
        if revision is not None:
            client.run_subcommand('checkout', path, cwd=checkout_path)
        else:
            client.run_subcommand('checkout', path, cwd=checkout_path)

        working_copy_path = os.path.join(checkout_path, os.path.basename(path))
        return SVNRepository(working_copy_path, cleanup=True)

class SVNRepository(Repository):
    def __init__(self, path, cleanup=False):
        self.path = path
        self.client = CommandLineClient('svn')
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

        result = self.client.run_subcommand('info', *args, flags=flags,
                                              cwd=self.path, **kwargs)
        return xmltodict.parse(result.stdout)['info']['entry']

    def walk_history(self):
        pass

    def get_changeset(self, rev=None):
        rev = int(rev)
        args = []
        if rev is not None:
            kwargs = {'r' : str(rev)}
        else:
            kwargs = {}
        flags = ['xml', 'v']

        result = self.client.run_subcommand('log', *args, flags=flags,
                                              cwd=self.path, **kwargs)
        out, err = result.stdout, result.stderr
        print(out, err)
        revision, author, timestamp, message, changes = self._read_log_xml(out)
        return ChangeSet(changes, None, revision, author, message, timestamp)

    def _read_log_xml(self, log):
        tree = ET.fromstring(log)

        author = tree.find('logentry/author').text
        date = tree.find('logentry/date').text
        message = tree.find('logentry/msg').text
        revision = int(tree.find('logentry').get('revision'))

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
                current_revision = str(revision)
                previous_path = None
                previous_revision = None
            elif action_string == 'C':
                action = ChangeType.copy
                current_path = path.text[1:]
                current_revision = str(revision)
                previous_path = path.get('copyfrom-path')[1:]
                previous_revision = path.get('copyfrom-rev')
            elif action_string == 'D':
                action = ChangeType.remove
                current_path = None
                current_revision = None
                previous_path = path.text[1:]
                previous_revision = str(revision - 1)
            elif action_string == 'M':
                action = ChangeType.modify
                current_path = path.text[1:]
                current_revision = str(revision)
                previous_path = path.text[1:]
                previous_revision = str(revision - 1)

            changes.append(Change(self, previous_path, previous_revision,
               current_path, current_revision, action))

        return revision, author, date, message, changes


    def get_object(self, path, rev=None):
        if rev:
            args = ['{path}@{rev}'.format(path=path, rev=rev)]
        else:
            args = [path]
        kwargs = {}
        flags = []
        result = self.client.run_subcommand('cat', *args, flags=flags,
                                              cwd=self.path, **kwargs)
        return result.stdout