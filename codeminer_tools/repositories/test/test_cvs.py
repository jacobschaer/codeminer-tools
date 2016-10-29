import mock
import os
import shlex
import shutil
import stat
import tempfile
import time
import unittest

from codeminer_tools.repositories import cvs, change
from test_utils import run_shell_command

global_commit_counter = 0


class TestCVSReads(unittest.TestCase):
    global_commit_counter = 0

    def generate_logmsg(self):
        global global_commit_counter
        global_commit_counter += 1
        return "Commit {commit}".format(commit=global_commit_counter)

    @classmethod
    def setUpClass(cls):
        cls.server_root = tempfile.mkdtemp()
        cls.source_root = tempfile.mkdtemp()
        perms = stat.S_ISVTX | (stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH) | \
                               (stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP) | \
                               (stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        os.chmod(cls.server_root, perms)
        os.mkdir(os.path.join(cls.server_root, 'test'))
        cls.env = {'CVSROOT': cls.server_root}
        run_shell_command('cvs init', cwd=cls.server_root, env=cls.env)
        cls.repo_working_directory = os.path.join(cls.source_root, 'test')
        repo = os.mkdir(cls.repo_working_directory)
        run_shell_command('cvs co test', cwd=cls.source_root, env=cls.env)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.server_root)
        shutil.rmtree(cls.source_root)

    def test_get_add_files(self):
        test_file_path = os.path.join(self.repo_working_directory, 'a.txt')
        with open(test_file_path, 'w') as test_file:
            test_file.write('a')
        run_shell_command(
            'cvs add a.txt',
            cwd=self.repo_working_directory,
            env=self.env)
        run_shell_command(
            'cvs commit -m "{commit}"'.format(
                commit=self.generate_logmsg()),
            cwd=self.repo_working_directory,
            env=self.env)
        sut = cvs.open_repository(self.repo_working_directory)
        version = sut.get_head_version('a.txt')
        changes = sut.get_changeset().changes
        self.assertEqual(
            changes, [
                change.Change(
                    sut, None, None, "a.txt", version, change.ChangeType.add)])

    def test_get_remove_files(self):
        test_file_path = os.path.join(self.repo_working_directory, 'r.txt')
        with open(test_file_path, 'w') as test_file:
            test_file.write('r')
        run_shell_command(
            'cvs add r.txt',
            cwd=self.repo_working_directory,
            env=self.env)
        run_shell_command(
            'cvs commit -m "{commit}"'.format(
                commit=self.generate_logmsg()),
            cwd=self.repo_working_directory,
            env=self.env)
        os.remove(test_file_path)
        run_shell_command(
            'cvs remove r.txt',
            cwd=self.repo_working_directory,
            env=self.env)
        run_shell_command(
            'cvs commit -m "{commit}"'.format(
                commit=self.generate_logmsg()),
            cwd=self.repo_working_directory,
            env=self.env)
        sut = cvs.open_repository(self.repo_working_directory)
        version = sut.get_head_version('r.txt')
        major, minor = version.split('.')
        previous_version = "{major}.{minor}".format(
            major=major, minor=(int(minor) - 1))
        changes = sut.get_changeset().changes
        self.assertEqual(
            changes, [
                change.Change(
                    sut, "r.txt", previous_version, "r.txt", version, change.ChangeType.remove)])

    def test_get_modify_files(self):
        test_file_path = os.path.join(self.repo_working_directory, 'm.txt')
        with open(test_file_path, 'w') as test_file:
            test_file.write('a')
        run_shell_command(
            'cvs add m.txt',
            cwd=self.repo_working_directory,
            env=self.env)
        run_shell_command(
            'cvs commit -m "{commit}"'.format(
                commit=self.generate_logmsg()),
            cwd=self.repo_working_directory,
            env=self.env)
        time.sleep(1)  # CVS commits aren't synchronous
        with open(test_file_path, 'a') as test_file:
            test_file.write('\nb\n')
        run_shell_command(
            'cvs commit -m "{commit}"'.format(
                commit=self.generate_logmsg()),
            cwd=self.repo_working_directory,
            env=self.env)
        sut = cvs.open_repository(self.repo_working_directory)
        version = sut.get_head_version('m.txt')
        major, minor = version.split('.')
        previous_version = "{major}.{minor}".format(
            major=major, minor=(int(minor) - 1))
        changes = sut.get_changeset().changes
        self.assertEqual(
            changes, [
                change.Change(
                    sut, "m.txt", previous_version, "m.txt", version, change.ChangeType.modify)])

    def test_get_module_name(self):
        sut = cvs.open_repository(self.repo_working_directory)
        self.assertEqual(
            sut.get_module_name(),
            os.path.basename(
                self.repo_working_directory))

    def test_get_object_at_head(self):
        test_file_path = os.path.join(self.repo_working_directory, 'b.txt')
        with open(test_file_path, 'wb') as test_file:
            test_file.write(b"asdf")
        run_shell_command(
            'cvs add b.txt',
            cwd=self.repo_working_directory,
            env=self.env)
        run_shell_command(
            'cvs commit -m "{commit}"'.format(
                commit=self.generate_logmsg()),
            cwd=self.repo_working_directory,
            env=self.env)
        sut = cvs.open_repository(self.repo_working_directory)
        file_obj = sut.get_file_contents("b.txt")
        self.assertEqual(file_obj.read(), b"asdf")

if __name__ == '__main__':
    unittest.main()
