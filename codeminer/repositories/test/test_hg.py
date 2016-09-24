import mock
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest

import codeminer.repositories.hg as hg
import codeminer.repositories.change as change

class TestHgReads(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repository_path = tempfile.mkdtemp()

        with open(os.path.join(cls.repository_path, "a.txt.orig"), "w") as a_file:
            a_file.write("a")

        with open(os.path.join(cls.repository_path, "b.txt.orig"), "w") as b_file:
            b_file.write("b")

        hg_config = ' -u "Test User <test@user.com>"'
        commands = [
            'hg init',
            'cp a.txt.orig a.txt',
            'hg add a.txt',
            'hg commit -m "Commit 1"' + hg_config,
            'cp b.txt.orig a.txt',
            'hg commit -m "Commit 2"' + hg_config,
            'hg copy a.txt b.txt',
            'hg commit -m "Commit 3"' + hg_config,
            'hg rename a.txt c.txt',
            'hg commit -m "Commit 4"' + hg_config,
            'hg remove c.txt',
            'hg commit -m "Commit 5"' + hg_config
        ]

        for command in commands:
            print(command)
            subprocess.run(shlex.split(command), cwd=cls.repository_path)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.repository_path)

    @mock.patch('codeminer.repositories.hg.hglib')
    @mock.patch('codeminer.repositories.hg.tempfile')
    def test_connect_local_repository(self, mock_tempfile, mock_hg):
        mock_tempfile.mkdtemp.return_value = 'destination'
        repository = hg.open_repository(self.repository_path)
        repository.cleanup = False
        mock.call.clone.assert_called_with(source=self.repository_path, dest="destination"),
        self.assertTrue(mock.call.clone.open.called)

    @mock.patch('codeminer.repositories.hg.hglib')
    @mock.patch('codeminer.repositories.hg.tempfile')
    def test_connect_remote_repository(self, mock_tempfile, mock_hg):
        mock_tempfile.mkdtemp.return_value = 'destination'
        repository = hg.open_repository("https://www.mercurial-scm.org/repo/hello")
        repository.cleanup = False
        mock.call.clone.assert_called_with(source="https://www.mercurial-scm.org/repo/hello", dest="destination"),
        self.assertTrue(mock.call.clone.open.called)

    def test_get_object_at_tip(self):
        sut = hg.open_repository(self.repository_path)
        file_object = sut.get_object("b.txt")
        self.assertEqual(file_object.read(), "b")

    def test_get_object_at_revision(self):
        sut = hg.open_repository(self.repository_path)
        file_object = sut.get_object("a.txt", rev=0)
        self.assertEqual(file_object.read(), "a")

    def test_get_changes(self):
        sut = hg.open_repository(self.repository_path)
        changeset = sut.get_changes('0')
        self.assertEqual(changeset,
            [change.Change(sut, None, None, "a.txt", '0', change.ChangeType.add)])

    def test_get_modify_change(self):
        sut = hg.open_repository(self.repository_path)
        changeset = sut.get_changes('1')
        self.assertEqual(changeset[0].action, change.ChangeType.modify)

    def test_get_copy_change(self):
        sut = hg.open_repository(self.repository_path)
        changeset = sut.get_changes('2')
        self.assertEqual(changeset[0].action, change.ChangeType.copy)

    def test_get_rename_change(self):
        sut = hg.open_repository(self.repository_path)
        changeset = sut.get_changes('3')
        self.assertEqual(changeset[0].action, change.ChangeType.move)

    def test_get_remove_change(self):
        sut = hg.open_repository(self.repository_path)
        changeset = sut.get_changes('4')
        self.assertEqual(changeset[0].action, change.ChangeType.remove)

    def test_walk_history(self):
        sut = hg.open_repository(self.repository_path)
        self.assertEqual(len([x for x in sut.walk_history()]), 5)

if __name__ == '__main__':
    unittest.main()