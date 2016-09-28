import os
import shutil
import subprocess

import xml.etree.ElementTree as ET

from codeminer.repositories.change import ChangeType, Change, ChangeSet
from codeminer.repositories.commandlineclient import CommandLineClient
from codeminer.repositories.repository import Repository

def open_repository(path, cvs_root=None, workspace=None, **kwargs):
    if os.path.exists(path):
        return CVSRepository(path, cvs_root=cvs_root)
    else:
        basename = os.path.basename(path)
        checkout_path = tempfile.mkdtemp(dir=workspace)
        client = CommandLineClient('cvs')
        client.run_subcommand('checkout', path, cwd=checkout_path)
        working_copy_path = os.path.join(checkout_path, os.path.basename(path))
        return CVSRepository(working_copy_path, cvs_root=cvs_root, cleanup=True)

class CVSRepository(Repository):
    def __init__(self, path, cvs_root=None, cleanup=False):
        env = os.environ.copy()
        if cvs_root is not None:
            env['CVSROOT'] = cvs_root

        self.client = CommandLineClient('cvs', env=env)
        self.path = path
        self.cleanup = cleanup

    def __del__(self):
        if self.cleanup:
            shutil.rmtree(self.path)

    @staticmethod
    def _cvs2cl(pipe, cwd=None, env=None):
        cvs2cl = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), '..', 'tools', 'cvs2cl.pl')

        return subprocess.Popen(['perl', cvs2cl, '--stdin', '--stdout', 
            '--xml', '--noxmlns', '--lines-modified', '--tags', '--follow'], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, stdin=pipe, cwd=cwd, env=env)

    def get_changeset(self, rev=None):
        args = []
        kwargs = {}
        flags = []
        if rev is not None:
            args.append('r{rev}'.format(revision=rev))

        out, err = self.client.run_subcommand('log', *args, flags=flags,
            cwd=self.path, pipe_out=self._cvs2cl, **kwargs)
        print(out, err)

        revision, author, timestamp, message, changes = self._read_log_xml(out)
        return ChangeSet(changes, None, revision, author, message, timestamp)

    def get_version(self, path):
        args = [path]
        kwargs = {}
        out, err = self.client.run_subcommand('status', *args, flags=flags,
                                              cwd=self.path, **kwargs)
        print(out)
        return re.match(r"Repository revision: +(\d+.\d+)", out).groups()[0]

    def _read_log_xml(self, log):
        tree = ET.fromstring(log)

        author = tree.find('entry/author').text
        date = tree.find('entry/isoDate').text
        message = tree.find('entry/msg').text

        changes = list()
        for path in tree.findall('entry/file'):
            state = path.find('cvsstate').text
            lines_added = path.find('linesadded')
            lines_removed = path.find('linesremoved')
            revision = path.find('revision').text
            name = path.find('name').text

            if lines_added:
                lines_added = lines_added.text
            if lines_removed:
                lines_removed = lines_removed.text

            if state == 'dead':
                # Removed
                action = ChangeType.remove
                current_path = None
                current_revision = None
                previous_path = name
                previous_revision = str(revision)
            else:
                # Added/Copied/Modified
                action = ChangeType.add
                current_path = name
                current_revision = str(revision)
                previous_path = None
                previous_revision = None

            changes.append(Change(self, previous_path, previous_revision,
               current_path, current_revision, action))

        return None, author, date, message, changes