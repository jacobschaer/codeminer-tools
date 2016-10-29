import datetime
from io import BytesIO
import os
import shlex
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

import xmltodict

from codeminer_tools.repositories.repository import Repository
from codeminer_tools.repositories.change import ChangeType, Change, ChangeSet
from codeminer_tools.clients.svn import SVNClient, SVNException


class SVNRepository(Repository):

    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if os.path.exists(path):
            self.working_copy = path
            self.cleanup = False
        else:
            basename = os.path.basename(path)
            revision = None
            if '@' in basename:
                basename, revision = basename.split('@')
            checkout_path = tempfile.mkdtemp(dir=self.workspace)
            client = SVNClient(username=self.username, password=self.password)
            client.checkout(path, cwd=checkout_path, quiet=True, revision=revision)
            self.working_copy = os.path.join(checkout_path, os.path.basename(path))
            self.cleanup = True
        self.client = SVNClient(username=self.username, password=self.password, cwd=self.working_copy)
        self.origin = self.info()['url']
        self.name = 'SVN'

    def __del__(self):
        if self.cleanup:
            try:
               shutil.rmtree(self.working_copy)
            except FileNotFoundError:
                pass

    def info(self, path=None, revision=None):
        if (path is not None) and (revision is not None):
            path = '{path}@{revision}'.format(
                path=path, revision=revision)

        out, err = self.client.info(xml=True, target=path, revision=revision)
        return xmltodict.parse(out)['info']['entry']

    def walk_history(self):
        out, err = self.client.log(xml=True, verbose=True)
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

    def get_properties(self, path, revision=None):
        out, err = self.client.proplist(path,
            xml=True, revision=revision, verbose=True)
        tree = ET.fromstring(out)
        properties = dict()
        for svnprop in tree.find('target').findall('property'):
            name = svnprop.get('name')
            value = svnprop.text
            properties[name] = value
        return properties

    def _read_log_xml(self, log):
        tree = ET.fromstring(log)
        for logentry in tree.findall('logentry'):
            yield self._read_logentry_xml(logentry)

    def _read_logentry_xml(self, logentry):
        # SVN does *not* require author, date, or messages... it's
        # unusual to not find one, but it can happen. None will have
        # to do for now.
        author = getattr(logentry.find('author'), 'text', None)
        date = getattr(logentry.find('date'), 'text', None)
        message = getattr(logentry.find('msg'), 'text', None)
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
            else:
                # Modify ('M') and Replace ('R')
                # Per SVN docs, 'replace' means:
                # > Item has been replaced in your working copy.
                # > This means the file was scheduled for deletion,
                # > and then a new file with the same name was scheduled
                # > for addition in its place.
                # If the commit had the copyfrom history, we would treat this
                # as a 'copy', but it didn't... so modify is a good approximation
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
