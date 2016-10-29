import mock
import os
import re
import shlex
import shutil
import stat
import subprocess
import tempfile
import time
import unittest

from codeminer_tools.clients import cvs

class TestCVSCommandLines(unittest.TestCase):
    @mock.patch('codeminer_tools.clients.commandline.subprocess.Popen')
    def test_add_single_file(self, commandline_mock):
        commandline_mock.return_value = mock.Mock(returncode=0, autospec=True)
        commandline_mock.return_value.communicate = mock.Mock(return_value = (None, None))

        self.sut = cvs.CVSClient(cwd='test_dir', cvs_root='test_root')
        self.sut.add(files='a.txt', message="asdf")
        args, kwargs = commandline_mock.call_args
        self.assertEqual((['cvs', 'add', '-m', '"asdf"', 'a.txt'],), args)
        self.assertEqual(kwargs['cwd'], 'test_dir')
        self.assertEqual(kwargs['env']['CVSROOT'], 'test_root')

    @mock.patch('codeminer_tools.clients.commandline.subprocess.Popen')
    def test_add_multiple_file(self, commandline_mock):
        commandline_mock.return_value = mock.Mock(returncode=0, autospec=True)
        commandline_mock.return_value.communicate = mock.Mock(return_value = (None, None))

        self.sut = cvs.CVSClient(cwd='test_dir', cvs_root='test_root')
        self.sut.add(files=['a.txt', 'b.txt'], message="asdf")
        args, kwargs = commandline_mock.call_args
        self.assertEqual((['cvs', 'add', '-m', '"asdf"', 'a.txt', 'b.txt'],), args)

    @mock.patch('codeminer_tools.clients.commandline.subprocess.Popen')
    def test_checkout_file(self, commandline_mock):
        commandline_mock.return_value = mock.Mock(returncode=0, autospec=True)
        commandline_mock.return_value.communicate = mock.Mock(return_value = (None, None))

        self.sut = cvs.CVSClient(cwd='test_dir', cvs_root='test_root')
        self.sut.checkout(path='a.txt', stdout=True)
        args, kwargs = commandline_mock.call_args
        self.assertEqual((['cvs', 'checkout', '-p', 'a.txt'],), args)

    @mock.patch('codeminer_tools.clients.commandline.subprocess.Popen')
    def test_commit(self, commandline_mock):
        commandline_mock.return_value = mock.Mock(returncode=0, autospec=True)
        commandline_mock.return_value.communicate = mock.Mock(return_value = (None, None))

        self.sut = cvs.CVSClient(cwd='test_dir', cvs_root='test_root')
        self.sut.commit("test message")
        args, kwargs = commandline_mock.call_args
        self.assertEqual((['cvs', 'commit', '-m', '"test message"'],), args)

    @mock.patch('codeminer_tools.clients.commandline.subprocess.Popen')
    def test_commit_files(self, commandline_mock):
        commandline_mock.return_value = mock.Mock(returncode=0, autospec=True)
        commandline_mock.return_value.communicate = mock.Mock(return_value = (None, None))

        self.sut = cvs.CVSClient(cwd='test_dir', cvs_root='test_root')
        self.sut.commit("test message", files=['a.txt', 'b.txt'])
        args, kwargs = commandline_mock.call_args
        self.assertEqual((['cvs', 'commit', '-m', '"test message"', 'a.txt', 'b.txt'],), args)


if __name__ == '__main__':
    unittest.main()