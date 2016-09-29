import hashlib
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

    def get_changeset(self, rev='HEAD'):
        args = ['-r{rev}'.format(rev=rev)]
        kwargs = {}
        flags = []

        out, err = self.client.run_subcommand('log', *args, flags=flags,
            cwd=self.path, pipe_out=self._cvs2cl, **kwargs)
        print(out, err)

        tags = None
        author, timestamp, message, changes = self._read_log_xml(out, limit=1)
        # There's no global revision ID in CVS, so make a commit ID
        revision_id = hashlib.md5(author.encode() + timestamp.encode() + message.encode()).hexdigest()
        return ChangeSet(changes, tags, revision_id, author, message, timestamp)

    def get_previous_version(self, version):
        # See: http://www.astro.princeton.edu/~rhl/cvs-branches.html
        components = [int(x) for x in version.split('.')]

        if len(components) == 2:
            # It's on the mainline branch
            major, minor = components
            if (minor == 0) or (minor == 1):
                return None
            else:
                return "{major}.{minor}".format(major=major, minor=(minor - 1))
        elif (components[-2] == 0 and components[-1] == 2):
            # It's the beginning of a branch
            return ".".join(components[:-2])
        else:
            components[-1] -= 1
            return ".".join(components)


        minor = int(minor)
        major = int(major)
        return "{major}.{minor}".format(major, minor - 1)

    def _read_log_xml(self, log, limit=None):
        tree = ET.fromstring(log)

        author = tree.find('entry/author').text
        date = tree.find('entry/isoDate').text
        message = tree.find('entry/msg').text

        changes = list()
        for count, path in enumerate(tree.findall('entry/file')):
            if limit is not None and count >= limit:
                break
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
                current_path = name
                current_revision = revision
                previous_path = name
                previous_revision = self.get_previous_version(revision)
            elif lines_added is None and lines_removed is None:
                action = ChangeType.add
                current_path = name
                current_revision = str(revision)
                previous_path = None
                previous_revision = None
            else:
                action = ChangeType.modify
                current_path = name
                current_revision = str(revision)
                previous_path = name
                previous_revision = self.get_previous_version(revision)

            changes.append(Change(self, previous_path, previous_revision,
               current_path, current_revision, action))

        return author, date, message, changes