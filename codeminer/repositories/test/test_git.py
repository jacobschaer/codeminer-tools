import mock
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest

import codeminer.repositories.git as git
import codeminer.repositories.change as change

class TestGitReads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repository_path = tempfile.mkdtemp()
        command = 'git init'
        subprocess.run(shlex.split(command), cwd=cls.repository_path)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.repository_path)

    def test_get_added_file(self):
        file_path = os.path.join(self.repository_path, 'a.txt')
        with open(file_path, 'w') as out_file:
            out_file.write("a")
        command = 'git add a.txt'
        subprocess.run(shlex.split(command), cwd=self.repository_path)
        command = 'git commit -m "Added file"'
        subprocess.run(shlex.split(command), cwd=self.repository_path)
        sut = git.open_repository(self.repository_path)
        print(sut.client.commit().message)
        changeset = sut.get_changeset()
        self.assertEqual(changeset.changes,
            [change.Change(sut, None, None, "a.txt", sut.client.commit().binsha, change.ChangeType.add)])



if __name__ == '__main__':
    unittest.main()