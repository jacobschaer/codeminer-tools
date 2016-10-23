import datetime
from io import BytesIO
import os
import shlex
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import xmltodict

from codeminer.repositories.repository import Repository
from codeminer.repositories.change import ChangeType, Change, ChangeSet
from codeminer.clients.svn import SVNClient


def open_repository(path, workspace=None, **kwargs):
    if os.path.exists(path):
        return SVNRepository(path)
    else:
        basename = os.path.basename(path)
        revision = None
        if '@' in basename:
            basename, revision = basename.split('@')
        checkout_path = tempfile.mkdtemp(dir=workspace)
        client = SVNClient()
        if revision is not None:
            client.checkout(path, quiet=True, cwd=checkout_path)
        else:
            client.checkout(path, quiet=True, cwd=checkout_path)

        working_copy_path = os.path.join(checkout_path, os.path.basename(path))
        return SVNRepository(working_copy_path, cleanup=True)


class SVNRepository(Repository):

    def __init__(self, path, cleanup=False):
        self.path = path
        self.client = SVNClient(cwd=self.path)
        self.cleanup = cleanup
        self.name = 'SVN'

    def __del__(self):
        if self.cleanup:
            shutil.rmtree(self.path)

    def info(self, path=None, revision=None):
        if (path is not None) and (revision is not None):
            path = '{path}@{revision}'.format(
                path=path, revision=revision)

        out, err = self.client.info(xml=True, target=path, revision=revision)
        return xmltodict.parse(out)['info']['entry']

    def walk_history(self):
        out, err = self.client.log(xml=True, verbose=True)
        print(out, err)
        for revision, author, timestamp, message, changes in self._read_log_xml(
                out):
            yield ChangeSet(changes, None, revision, author, message, timestamp)

    def get_changeset(self, revision=None):
        out, err = self.client.log(
            xml=True, revision=revision, verbose=True, limit=1)
        print(out, err)
        revision, author, timestamp, message, changes = self._read_log_xml(
            out).__next__()
        return ChangeSet(changes, None, revision, author, message, timestamp)

    def _read_log_xml(self, log):
        tree = ET.fromstring(log)
        for logentry in tree.findall('logentry'):
            yield self._read_logentry_xml(logentry)

    def _read_logentry_xml(self, logentry):
        author = logentry.find('author').text
        date = logentry.find('date').text
        message = logentry.find('msg').text
        revision = int(logentry.get('revision'))

        changes = list()
        for path in logentry.find('paths'):
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

    def get_file_contents(self, path, revision=None):
        if revision:
            path = '{path}@{revision}'.format(path=path, revision=revision)
        # , ignore_keywords=True only works SVN 1.7+
        out, err = self.client.cat(path)
        return BytesIO(out)
