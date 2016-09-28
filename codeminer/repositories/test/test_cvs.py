import mock
import os
import shlex
import shutil
import stat
import subprocess
import tempfile
import unittest

from codeminer.repositories import cvs, change
from test_utils import run_shell_command

class TestCVSReads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_root = tempfile.mkdtemp()
        cls.source_root = tempfile.mkdtemp()
        perms = stat.S_ISVTX | (stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH) | \
                               (stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP) | \
                               (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        os.chmod(cls.server_root, perms)
        os.mkdir(os.path.join(cls.server_root, 'test'))
        cls.env = {'CVSROOT' : cls.server_root}
        run_shell_command('cvs init', cwd=cls.server_root, env=cls.env)
        cls.repo_working_directory = os.path.join(cls.source_root, 'test')
        repo = os.mkdir(cls.repo_working_directory)
        run_shell_command('cvs co test', cwd=cls.source_root, env=cls.env)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.server_root)
        shutil.rmtree(cls.source_root)

    def test_get_add_files(self):
        test_file = os.path.join(self.repo_working_directory, 'a.txt')
        with open(test_file, 'w') as test_file:
            test_file.write('a')
        run_shell_command('cvs add a.txt', cwd=self.repo_working_directory, env=self.env)
        run_shell_command('cvs commit -m "Test"', cwd=self.repo_working_directory, env=self.env)
        sut = cvs.open_repository(self.repo_working_directory)
        changes = sut.get_changeset().changes
        self.assertEqual(changes, [change.Change(sut, None, None, "a.txt", '1.1', change.ChangeType.add)])

    # def test_get_remove_files(self):
    #     test_file = os.path.join(self.repo_working_directory, 'a.txt')
    #     with open(test_file, 'w') as test_file:
    #         test_file.write('a')
    #     run_shell_command('svn add a.txt', cwd=self.repo_working_directory)
    #     run_shell_command('svn commit -m "Test"', cwd=self.repo_working_directory)
    #     run_shell_command('svn rm a.txt', cwd=self.repo_working_directory)
    #     run_shell_command('svn commit -m "Test"', cwd=self.repo_working_directory)
    #     run_shell_command('svn up', cwd=self.repo_working_directory)
    #     sut = svn.open_repository(self.repo_working_directory)
    #     revision = sut.info()['commit']['@revision']
    #     changes = sut.get_changeset(revision).changes
    #     self.assertEqual(changes, [change.Change(sut, "a.txt", str(int(revision) - 1), None, None, change.ChangeType.remove)])

    # def test_get_copy_files(self):
    #     test_file = os.path.join(self.repo_working_directory, 'a.txt')
    #     with open(test_file, 'w') as test_file:
    #         test_file.write('a')
    #     run_shell_command('svn add a.txt', cwd=self.repo_working_directory)
    #     run_shell_command('svn commit -m "Test"', cwd=self.repo_working_directory)
    #     run_shell_command('svn cp a.txt b.txt', cwd=self.repo_working_directory)
    #     run_shell_command('svn commit -m "Test"', cwd=self.repo_working_directory)
    #     run_shell_command('svn up', cwd=self.repo_working_directory)
    #     sut = svn.open_repository(self.repo_working_directory)
    #     revision = sut.info()['commit']['@revision']
    #     changes = sut.get_changeset(revision).changes
    #     self.assertEqual(changes, [change.Change(sut, "a.txt", str(int(revision) - 1), "b.txt", revision, change.ChangeType.copy)])

    # def test_get_modified_files(self):
    #     test_file_path = os.path.join(self.repo_working_directory, 'a.txt')
    #     with open(test_file_path, 'w') as test_file:
    #         test_file.write('a')
    #     run_shell_command('svn add a.txt', cwd=self.repo_working_directory)
    #     run_shell_command('svn commit -m "Test"', cwd=self.repo_working_directory)
    #     with open(test_file_path, 'w') as test_file:
    #         test_file.write('b')
    #     run_shell_command('svn commit -m "Test"', cwd=self.repo_working_directory)
    #     run_shell_command('svn up', cwd=self.repo_working_directory)
    #     sut = svn.open_repository(self.repo_working_directory)
    #     revision = sut.info()['commit']['@revision']
    #     changes = sut.get_changeset(revision).changes
    #     self.assertEqual(changes, [change.Change(sut, "a.txt", str(int(revision) - 1), "a.txt", revision, change.ChangeType.modify)])

    # def test_get_object(self):
    #     test_file_path = os.path.join(self.repo_working_directory, 'a.txt')
    #     with open(test_file_path, 'wb') as test_file:
    #         test_file.write(b'a')
    #     run_shell_command('svn add a.txt', cwd=self.repo_working_directory)
    #     run_shell_command('svn commit -m "Test"', cwd=self.repo_working_directory)
    #     run_shell_command('svn up', cwd=self.repo_working_directory)
    #     sut = svn.open_repository(self.repo_working_directory)
    #     revision = sut.info()['commit']['@revision']
    #     self.assertEqual(sut.get_object('a.txt', rev=revision), b'a')


if __name__ == '__main__':
    unittest.main()