import mock
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest

import codeminer.repositories.svn as svn
import codeminer.repositories.change as change

from test_utils import run_shell_command

class TestSVNReads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_name = 'test_repo'
        cls.server_root = tempfile.mkdtemp()
        cls.checkout_root = tempfile.mkdtemp()
        cls.repo_url = 'file://{server_root}/{repo_name}'.format(
            server_root=cls.server_root, repo_name=cls.repo_name)
        cls.repo_working_directory = os.path.join(cls.checkout_root, cls.repo_name)
        run_shell_command('svnadmin create {repo_name}'.format(
            repo_name = cls.repo_name), cwd=cls.server_root)
        run_shell_command('svn co "{repo_url}"'.format(repo_url = cls.repo_url),
            cwd=cls.checkout_root)
    
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.server_root)
        shutil.rmtree(cls.checkout_root)

    def tearDown(self):
        for path in os.listdir(self.repo_working_directory):
            if path != '.svn':
                run_shell_command('svn rm {path} --force -q'.format(path=path),
                    cwd=self.repo_working_directory)
        run_shell_command('svn commit -m "Cleanup"', cwd=self.repo_working_directory)
        run_shell_command('svn up', cwd=self.repo_working_directory)

    def test_get_info(self):
        sut = svn.open_repository(self.repo_working_directory)
        info = sut.info()
        print(info)
        self.assertEqual(info['url'], self.repo_url)
        self.assertEqual(info['repository']['root'], self.repo_url)
        self.assertEqual(info['wc-info']['wcroot-abspath'], sut.path)
        self.assertTrue(int(info['commit']['@revision']) >= 0)

    def test_get_add_files(self):
        test_file = os.path.join(self.repo_working_directory, 'a.txt')
        with open(test_file, 'w') as test_file:
            test_file.write('a')
        run_shell_command('svn add a.txt', cwd=self.repo_working_directory)
        run_shell_command('svn commit -m "Test"', cwd=self.repo_working_directory)
        run_shell_command('svn up', cwd=self.repo_working_directory)
        sut = svn.open_repository(self.repo_working_directory)
        revision = sut.info()['commit']['@revision']
        changes = sut.get_changes(revision)
        self.assertEqual(changes, [change.Change(sut, None, None, "a.txt", revision, change.ChangeType.add)])

    def test_get_remove_files(self):
        test_file = os.path.join(self.repo_working_directory, 'a.txt')
        with open(test_file, 'w') as test_file:
            test_file.write('a')
        run_shell_command('svn add a.txt', cwd=self.repo_working_directory)
        run_shell_command('svn commit -m "Test"', cwd=self.repo_working_directory)
        run_shell_command('svn rm a.txt', cwd=self.repo_working_directory)
        run_shell_command('svn commit -m "Test"', cwd=self.repo_working_directory)
        run_shell_command('svn up', cwd=self.repo_working_directory)
        sut = svn.open_repository(self.repo_working_directory)
        revision = sut.info()['commit']['@revision']
        changes = sut.get_changes(revision)
        self.assertEqual(changes, [change.Change(sut, "a.txt", str(int(revision) - 1), None, None, change.ChangeType.remove)])

    def test_get_copy_files(self):
        test_file = os.path.join(self.repo_working_directory, 'a.txt')
        with open(test_file, 'w') as test_file:
            test_file.write('a')
        run_shell_command('svn add a.txt', cwd=self.repo_working_directory)
        run_shell_command('svn commit -m "Test"', cwd=self.repo_working_directory)
        run_shell_command('svn cp a.txt b.txt', cwd=self.repo_working_directory)
        run_shell_command('svn commit -m "Test"', cwd=self.repo_working_directory)
        run_shell_command('svn up', cwd=self.repo_working_directory)
        sut = svn.open_repository(self.repo_working_directory)
        revision = sut.info()['commit']['@revision']
        changes = sut.get_changes(revision)
        self.assertEqual(changes, [change.Change(sut, "a.txt", str(int(revision) - 1), "b.txt", revision, change.ChangeType.copy)])

    def test_get_modified_files(self):
        test_file_path = os.path.join(self.repo_working_directory, 'a.txt')
        with open(test_file_path, 'w') as test_file:
            test_file.write('a')
        run_shell_command('svn add a.txt', cwd=self.repo_working_directory)
        run_shell_command('svn commit -m "Test"', cwd=self.repo_working_directory)
        with open(test_file_path, 'w') as test_file:
            test_file.write('b')
        run_shell_command('svn commit -m "Test"', cwd=self.repo_working_directory)
        run_shell_command('svn up', cwd=self.repo_working_directory)
        sut = svn.open_repository(self.repo_working_directory)
        revision = sut.info()['commit']['@revision']
        changes = sut.get_changes(revision)
        self.assertEqual(changes, [change.Change(sut, "a.txt", str(int(revision) - 1), "a.txt", revision, change.ChangeType.modify)])

    def test_get_object(self):
        test_file_path = os.path.join(self.repo_working_directory, 'a.txt')
        with open(test_file_path, 'wb') as test_file:
            test_file.write(b'a')
        run_shell_command('svn add a.txt', cwd=self.repo_working_directory)
        run_shell_command('svn commit -m "Test"', cwd=self.repo_working_directory)
        run_shell_command('svn up', cwd=self.repo_working_directory)
        sut = svn.open_repository(self.repo_working_directory)
        revision = sut.info()['commit']['@revision']
        self.assertEqual(sut.get_object('a.txt', rev=revision), b'a')

if __name__ == '__main__':
    unittest.main()