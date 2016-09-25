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
            command.append('{dashes}{flag} {value}'.format(dashes=dashes,
               flag=flag, value=value))

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
        pass