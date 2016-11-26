import mock
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest

import codeminer_tools.repositories.svn as svn
import codeminer_tools.repositories.change as change
from codeminer_tools.repositories.entity import EntityType

from test_utils import run_shell_command


class TestSVNReads(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo_name = 'test_repo'
        cls.server_root = tempfile.mkdtemp()
        cls.checkout_root = tempfile.mkdtemp()
        cls.repo_url = 'file://{server_root}/{repo_name}'.format(
            server_root=cls.server_root, repo_name=cls.repo_name)
        cls.repo_working_directory = os.path.join(
            cls.checkout_root, cls.repo_name)
        run_shell_command('svnadmin create {repo_name}'.format(
            repo_name=cls.repo_name), cwd=cls.server_root)
        run_shell_command('svn co "{repo_url}"'.format(repo_url=cls.repo_url),
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
        run_shell_command(
            'svn commit -m "Cleanup"',
            cwd=self.repo_working_directory)
        run_shell_command('svn up', cwd=self.repo_working_directory)

    def test_get_info(self):
        sut = svn.SVNRepository(self.repo_working_directory)
        info = sut.info()
        print(info)
        self.assertEqual(info['url'], self.repo_url)
        self.assertEqual(info['repository']['root'], self.repo_url)
        #self.assertEqual(info['wc-info']['wcroot-abspath'], sut.path)
        self.assertTrue(int(info['commit']['@revision']) >= 0)

    def test_get_add_files(self):
        test_file = os.path.join(self.repo_working_directory, 'a.txt')
        with open(test_file, 'w') as test_file:
            test_file.write('a')
        run_shell_command('svn add a.txt', cwd=self.repo_working_directory)
        run_shell_command(
            'svn commit -m "Test"',
            cwd=self.repo_working_directory)
        run_shell_command('svn up', cwd=self.repo_working_directory)
        sut = svn.SVNRepository(self.repo_working_directory)
        revision = sut.info()['commit']['@revision']
        changes = sut.get_changeset(revision).changes
        self.assertEqual(
            changes, [
                change.Change(
                    sut, None, None, EntityType.file, "a.txt", revision, EntityType.file, change.ChangeType.add)])

    def test_get_remove_files(self):
        test_file = os.path.join(self.repo_working_directory, 'a.txt')
        with open(test_file, 'w') as test_file:
            test_file.write('a')
        run_shell_command('svn add a.txt', cwd=self.repo_working_directory)
        run_shell_command(
            'svn commit -m "Test"',
            cwd=self.repo_working_directory)
        run_shell_command('svn rm a.txt', cwd=self.repo_working_directory)
        run_shell_command(
            'svn commit -m "Test"',
            cwd=self.repo_working_directory)
        run_shell_command('svn up', cwd=self.repo_working_directory)
        sut = svn.SVNRepository(self.repo_working_directory)
        revision = sut.info()['commit']['@revision']
        changes = sut.get_changeset(revision).changes
        self.assertEqual(
            changes, [
                change.Change(
                    sut, "a.txt", str(
                        int(revision) - 1), EntityType.file, None, None, None, change.ChangeType.remove)])

    def test_get_copy_files(self):
        test_file = os.path.join(self.repo_working_directory, 'a.txt')
        with open(test_file, 'w') as test_file:
            test_file.write('a')
        run_shell_command('svn add a.txt', cwd=self.repo_working_directory)
        run_shell_command(
            'svn commit -m "Test"',
            cwd=self.repo_working_directory)
        run_shell_command(
            'svn cp a.txt b.txt',
            cwd=self.repo_working_directory)
        run_shell_command(
            'svn commit -m "Test"',
            cwd=self.repo_working_directory)
        run_shell_command('svn up', cwd=self.repo_working_directory)
        sut = svn.SVNRepository(self.repo_working_directory)
        revision = sut.info()['commit']['@revision']
        changes = sut.get_changeset(revision).changes
        self.assertEqual(
            changes, [
                change.Change(
                    sut, "a.txt", str(
                        int(revision) - 1), EntityType.file, "b.txt", revision, EntityType.file, change.ChangeType.copy)])

    def test_get_modified_files(self):
        test_file_path = os.path.join(self.repo_working_directory, 'a.txt')
        with open(test_file_path, 'w') as test_file:
            test_file.write('a')
        run_shell_command('svn add a.txt', cwd=self.repo_working_directory)
        run_shell_command(
            'svn commit -m "Test"',
            cwd=self.repo_working_directory)
        with open(test_file_path, 'w') as test_file:
            test_file.write('b')
        run_shell_command(
            'svn commit -m "Test"',
            cwd=self.repo_working_directory)
        run_shell_command('svn up', cwd=self.repo_working_directory)
        sut = svn.SVNRepository(self.repo_working_directory)
        revision = sut.info()['commit']['@revision']
        changes = sut.get_changeset(revision).changes
        self.assertEqual(
                changes, [
                    change.Change(
                        sut, "a.txt", str(
                            int(revision) - 1), EntityType.file, "a.txt", revision, EntityType.file, change.ChangeType.modify)])

    def test_get_file_contents(self):
        test_file_path = os.path.join(self.repo_working_directory, 'a.txt')
        with open(test_file_path, 'wb') as test_file:
            test_file.write(b'a')
        run_shell_command('svn add a.txt', cwd=self.repo_working_directory)
        run_shell_command(
            'svn commit -m "Test"',
            cwd=self.repo_working_directory)
        run_shell_command('svn up', cwd=self.repo_working_directory)
        sut = svn.SVNRepository(self.repo_working_directory)
        revision = sut.info()['commit']['@revision']
        self.assertEqual(
            sut.get_file_contents(
                'a.txt',
                revision=revision).read(),
            b'a')

    def test_get_properties(self):
        test_file_path = os.path.join(self.repo_working_directory, 'a.txt')
        with open(test_file_path, 'wb') as test_file:
            test_file.write(b'a')
        run_shell_command('svn add a.txt', cwd=self.repo_working_directory)
        run_shell_command('svn propset a:b c a.txt', cwd=self.repo_working_directory)
        run_shell_command(
            'svn commit -m "Test"',
            cwd=self.repo_working_directory)
        run_shell_command('svn up', cwd=self.repo_working_directory)
        sut = svn.SVNRepository(self.repo_working_directory)
        revision = sut.info()['commit']['@revision']
        self.assertTrue(('a:b', 'c') in sut.get_properties('a.txt', revision=revision).items())

    def test_get_directory_add(self):
        test_dir_path = os.path.join(self.repo_working_directory, 'a')
        os.makedirs(test_dir_path)
        run_shell_command('svn add a', cwd=self.repo_working_directory)
        run_shell_command(
            'svn commit -m "Test"',
            cwd=self.repo_working_directory)
        run_shell_command('svn up', cwd=self.repo_working_directory)
        sut = svn.SVNRepository(self.repo_working_directory)
        revision = sut.info()['commit']['@revision']
        changes = sut.get_changeset(revision).changes
        self.assertEqual(
                changes, [
                    change.Change(
                        sut, None, None, None, "a", revision, EntityType.directory, change.ChangeType.add)])

if __name__ == '__main__':
    unittest.main()
