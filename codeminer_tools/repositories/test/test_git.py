import mock
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest

import codeminer_tools.repositories.git as git
import codeminer_tools.repositories.change as change
from codeminer_tools.repositories.entity import EntityType


class TestGitReads(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repository_path = tempfile.mkdtemp()
        cls.test_env = {
            'GIT_AUTHOR_NAME': 'Test Author',
            'GIT_AUTHOR_EMAIL': 'test@test.com',
            'GIT_COMMITTER_NAME': 'Test Commiter',
            'EMAIL': 'test@test.com'
        }
        command = 'git init'
        subprocess.run(
            shlex.split(command),
            cwd=cls.repository_path,
            env=cls.test_env)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.repository_path)

    def tearDown(self):
        command = 'git rm -f test.txt'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        command = 'git commit -m "Resetting Test File"'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)

    def test_get_added_file(self):
        file_path = os.path.join(self.repository_path, 'test.txt')
        with open(file_path, 'w') as out_file:
            out_file.write("a")
        command = 'git add test.txt'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        command = 'git commit -m "Test Added file"'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        sut = git.open_repository(self.repository_path)
        changeset = sut.get_changeset()
        revision = sut.client.commit().binsha
        self.assertEqual(
            changeset.changes, [
                change.Change(
                    sut, None, None, None, "test.txt", revision, EntityType.file, change.ChangeType.add)])

    def test_get_removed_file(self):
        sut = git.open_repository(self.repository_path)
        file_path = os.path.join(self.repository_path, 'test.txt')
        with open(file_path, 'w') as out_file:
            out_file.write("a")
        command = 'git add test.txt'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        command = 'git commit -m "Test Remove file - initial add"'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        revision = sut.client.commit().binsha
        command = 'git rm -f test.txt'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        command = 'git commit -m "Test Remove file - remove file"'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        changeset = sut.get_changeset()
        self.assertEqual(
            changeset.changes, [
                change.Change(
                    sut, "test.txt", revision, EntityType.file, None, None, None, change.ChangeType.remove)])

    def test_get_modified_file(self):
        sut = git.open_repository(self.repository_path)
        file_path = os.path.join(self.repository_path, 'test.txt')
        with open(file_path, 'w') as out_file:
            out_file.write("a")
        command = 'git add test.txt'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        command = 'git commit -m "Added file"'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        revision_a = sut.client.commit().binsha
        with open(file_path, 'w') as out_file:
            out_file.write("b")
        command = 'git add test.txt'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        command = 'git commit -m "Updated file"'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        revision_b = sut.client.commit().binsha
        changeset = sut.get_changeset()
        self.assertEqual(
            changeset.changes, [
                change.Change(
                    sut, "test.txt", revision_a, EntityType.file, "test.txt", revision_b, EntityType.file, change.ChangeType.modify)])

    def test_get_move_file(self):
        sut = git.open_repository(self.repository_path)
        file_path = os.path.join(self.repository_path, 'test_old.txt')
        with open(file_path, 'w') as out_file:
            out_file.write("a")
        command = 'git add test_old.txt'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        command = 'git commit -m "Added file"'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        revision_a = sut.client.commit().binsha
        command = 'git mv test_old.txt test.txt'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        command = 'git commit -m "Updated file"'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        revision_b = sut.client.commit().binsha
        changeset = sut.get_changeset()
        self.assertEqual(
            changeset.changes, [
                change.Change(
                    sut, "test_old.txt", revision_a, EntityType.file, "test.txt", revision_b, EntityType.file, change.ChangeType.move)])

    def test_get_copied_file(self):
        sut = git.open_repository(self.repository_path)
        old_file_path = os.path.join(self.repository_path, 'test_old.txt')
        new_file_path = os.path.join(self.repository_path, 'test.txt')
        with open(old_file_path, 'w') as out_file:
            out_file.write("a")
        command = 'git add test_old.txt'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        command = 'git commit -m "Added file"'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        revision_a = sut.client.commit().binsha
        shutil.copyfile(old_file_path, new_file_path)
        command = 'git add test.txt'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        command = 'git commit -m "Updated file"'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        revision_b = sut.client.commit().binsha
        changeset = sut.get_changeset()
        self.assertEqual(
            changeset.changes, [
                change.Change(
                    sut, "test_old.txt", revision_a, EntityType.file, "test.txt", revision_b, EntityType.file, change.ChangeType.copy)])

    def test_get_derived_file(self):
        sut = git.open_repository(self.repository_path)
        old_file_path = os.path.join(self.repository_path, 'test_old.txt')
        new_file_path = os.path.join(self.repository_path, 'test.txt')
        with open(old_file_path, 'w') as out_file:
            out_file.write("abcdefghijklmnopqrstuvwxyz\n" * 100)
        command = 'git add test_old.txt'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        command = 'git commit -m "Test Derive: Added file"'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        revision_a = sut.client.commit().binsha
        with open(new_file_path, 'w') as out_file:
            out_file.write("abcdefghijklmnopqrstuvwxyz\n" * 110)
        command = 'git rm -r test_old.txt'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        command = 'git add test.txt'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        command = 'git commit -m "Test Derive: Updated file"'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        revision_b = sut.client.commit().binsha
        print(sut.client.commit().message)
        changeset = sut.get_changeset()
        self.assertEqual(changeset.changes,
                         [change.Change(sut,
                                        "test_old.txt",
                                        revision_a,
                                        EntityType.file,
                                        "test.txt",
                                        revision_b,
                                        EntityType.file,
                                        change.ChangeType.derived)])

    def test_get_contents_at_head(self):
        file_path = os.path.join(self.repository_path, 'test.txt')
        with open(file_path, 'w') as out_file:
            out_file.write("ab")
        command = 'git add test.txt'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        command = 'git commit -m "Added file"'
        subprocess.run(
            shlex.split(command),
            cwd=self.repository_path,
            env=self.test_env)
        sut = git.open_repository(self.repository_path)
        contents = sut.get_file_contents('test.txt')
        self.assertEqual(contents.read(), b"ab")

if __name__ == '__main__':
    unittest.main()
