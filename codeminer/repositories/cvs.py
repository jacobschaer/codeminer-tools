import hashlib
from io import BytesIO
import os
import shutil
import subprocess
from typing import Dict, List, Optional, Union, Tuple

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

class CVSException(Exception):
    pass


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
            '--xml', '--noxmlns', '--lines-modified', '--tags', '--follow'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=pipe,
            cwd=cwd, env=env)

    def add(self, files : Union[List[str], str], message : str = None,
        rcs_kflag : str = None, *args : str, **kwargs : str) -> Tuple[str,str]:
        """Add a new file/directory to the repository

        Parameters
        ----------
        files : str or list of str
            Files to be added
        message : str, optional
            Use this "message" for the creation log
        rcs_kflag : str, optional
            Add the file with the specified kflag.

        Returns
        -------
        stdout : str
            The standard output from the cvs command
        stderr : str
            The error output from the cvs command

        Raises
        ------
        CVSException
            If the cvs program returns an error code

        """
        options = {}
        flags = []
        arguments = []

        if type(files) == str:
            arguments.append(files)
        else:
            arguments += files

        if message is not None:
            options['m'] = message

        if rcs_kflag is not None:
            options['k'] = rcs_kflag

        for arg in args:
            flags.append(arg)

        for kwarg in kwargs:
            options[kwarg] = kwargs[kwarg]

        result = self.client.run_subcommand('add', *arguments, flags=flags,
            cwd=self.path, **options)
        if result.returncode != 0:
            raise CVSException(result.stderr)
        else:
            return result.stdout, result.stderr

    def checkout(self, path : str = None,
        reset : bool = False, no_shorten : bool = False, prune : bool = False,
        recursive : bool = False, cat : bool = False, force : bool = False,
        local_directory : bool = False, no_module : bool = False,
        stdout : bool = False, status : bool = False, revision : str = None,
        date : str = None, dir : str = None, kopt : str = None,
        merge : bool = None, *args : str, **kwargs : str) -> Tuple[str,str]:
        """Checkout sources for editing

        Parameters
        ----------
        reset : bool
            Reset any sticky tags/date/kopts.
        no_shorten : bool
            Don't shorten module paths if -d specified.
        prune : bool
            Prune empty directories.
        recursive : bool
            Process directories recursively.
        cat : bool
            "cat" the module database.
        force : bool
            Force a head revision match if tag/date not found.
        local_directory : bool
            Local directory only, not recursive
        no_module : bool
            Do not run module program (if any).
        stdout : bool
            Check out files to standard output (avoids stickiness).
        status : bool
            Like -c, but include module status.
        revision : str
            Check out revision or tag. (implies -P) (is sticky)
        date : str
            Check out revisions as of date. (implies -P) (is sticky)
        dir : str
            Check out into dir instead of module name.
        kopt : str
            Use RCS kopt -k option on checkout. (is sticky)
        merge : str
            Merge in changes made between current revision and rev.

        Returns
        -------
        stdout : str
            The standard output from the cvs command
        stderr : str
            The error output from the cvs command

        Raises
        ------
        CVSException
            If the cvs program returns an error code

        """
        options = {}
        flags = []
        arguments = []

        if path is not None:
            arguments.append(path)

        if reset:
            flags.append('A')
        if no_shorten:
            flags.append('N')
        if prune:
            flags.append('P')
        if recursive:
            flags.append('R')
        if cat:
            flags.append('c')
        if force:
            flags.append('f')
        if local_directory:
            flags.append('l')
        if no_module:
            flags.append('n')
        if stdout:
            flags.append('p')
        if status:
            flags.append('s')

        if revision is not None:
            options['r'] = revision
        if date is not None:
            options['D'] = date
        if dir is not None:
            options['d'] = dir
        if kopt is not None:
            options['k'] = kopt
        if merge is not None:
            options['j'] = merge

        for arg in args:
            flags.append(arg)

        for kwarg in kwargs:
            options[kwarg] = kwargs[kwarg]

        result = self.client.run_subcommand('checkout', *arguments, flags=flags,
            cwd=self.path, **options)
        if result.returncode != 0:
            raise CVSException(result.stderr)
        else:
            return result.stdout, result.stderr

    def commit(self, message : str, files : Union[List[str], str] = [],
        recursive : bool = False, local_directory : bool = False,
        force : bool = False, revision : str = None,
        *args : str, **kwargs : str) -> Tuple[str,str]:
        """Check files into the repository

        Parameters
        ----------
        message : str
            Log message.
        files : str or list of str, optional
            Files to be commited, default is current working directory
        recursive : bool, optional
            Process directories recursively.
        local_directory : bool, optional
            Local directory only (not recursive).
        force: bool, optional
            Force the file to be committed; disables recursion.
        revision : str, optional
            Commit to this branch or trunk revision.

        Returns
        -------
        stdout : str
            The standard output from the cvs command
        stderr : str
            The error output from the cvs command

        Raises
        ------
        CVSException
            If the cvs program returns an error code

        """
        options = {}
        flags = []
        arguments = []

        if type(files) == str:
            arguments.append(files)
        else:
            arguments += files

        options['m'] = message

        if recursive:
            flags.append('R')
        if local_directory:
            flags.append('l') 
        if force:
            flags.append('f')
        if revision is not None:
            options['r'] = revision

        for arg in args:
            flags.append(arg)

        for kwarg in kwargs:
            options[kwarg] = kwargs[kwarg]

        result = self.client.run_subcommand('commit', *arguments, flags=flags,
            cwd=self.path, **options)
        if result.returncode != 0:
            raise CVSException(result.stderr)
        else:
            return result.stdout, result.stderr

    def remove(self, files : Union[List[str], str] = [],
        delete : bool = False, local_directory : bool = False,
        recursive : bool = False, *args : str, **kwargs : str):
        """Remove an entry from the repository

        Parameters
        ----------
        files : str or list of str, optional
            Files to be commited, default is current working directory
        delete : bool, optional
            Delete the file before removing it.
        local_directory : bool, optional
            Process this directory only (not recursive).
        recursive : bool, optional
            Process directories recursively.

        Raises
        ------

        """
        options = {}
        flags = []
        arguments = []

        if type(files) == str:
            arguments.append(files)
        else:
            arguments += files

        if delete:
            flags.append('f')
        if local_directory:
            flags.append('l') 
        if recursive:
            flags.append('R')

        for arg in args:
            flags.append(arg)

        for kwarg in kwargs:
            options[kwarg] = kwargs[kwarg]

        result = self.client.run_subcommand('remove', *arguments, flags=flags,
            cwd=self.path, **options)
        if result.returncode != 0:
            raise CVSException(result.stderr)
        else:
            return result.stdout, result.stderr

    def get_changeset(self, rev='HEAD'):
        args = ['-r{rev}'.format(rev=rev)]
        kwargs = {}
        flags = []

        p1,p2 = self.client.run_subcommand('log', *args, flags=flags,
            cwd=self.path, pipe_out=self._cvs2cl, **kwargs)
        out, err, exit = p2.stdout, p2.stderr, p2.returncode
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

    def get_object(self, path, revision=None):
        repository_name = self._get_repository_name()
        real_path = os.path.join(repository_name, path)
        out, stderr = self.checkout(
            path = real_path, 
            stdout = True,
            revision = revision
        )
        return BytesIO(out)

    def _get_repository_name(self):
        """ It's possible that the directory containing the local copy does
        not have the same name as the "module" (see the -d flag). Fortunately
        we can recover the name by peeking into the CVS filesystem"""
        repository_file_path = os.path.join(self.path, 'CVS', 'Repository')
        with open(repository_file_path, 'r') as repository_file:
            return repository_file.read().strip()

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