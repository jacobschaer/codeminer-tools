import mock
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest

from codeminer_tools.repositories import hg, change


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
            'hg commit -m "Commit 5"' + hg_config,
            'hg copy b.txt d.txt',
            'cp a.txt.orig d.txt',
            'hg commit -m "Commit 6"' + hg_config
        ]

        for command in commands:
            print(command)
            subprocess.run(shlex.split(command), cwd=cls.repository_path)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.repository_path)

    @mock.patch('codeminer_tools.repositories.hg.hglib')
    @mock.patch('codeminer_tools.repositories.hg.tempfile')
    def test_connect_local_repository(self, mock_tempfile, mock_hg):
        mock_tempfile.mkdtemp.return_value = 'destination'
        repository = hg.open_repository(self.repository_path)
        repository.cleanup = False
        mock.call.clone.assert_called_with(
            source=self.repository_path, dest="destination"),
        self.assertTrue(mock.call.clone.open.called)

    @mock.patch('codeminer_tools.repositories.hg.hglib')
    @mock.patch('codeminer_tools.repositories.hg.tempfile')
    def test_connect_remote_repository(self, mock_tempfile, mock_hg):
        mock_tempfile.mkdtemp.return_value = 'destination'
        repository = hg.open_repository(
            "https://www.mercurial-scm.org/repo/hello")
        repository.cleanup = False
        mock.call.clone.assert_called_with(
            source="https://www.mercurial-scm.org/repo/hello",
            dest="destination"),
        self.assertTrue(mock.call.clone.open.called)

    def test_get_object_at_tip(self):
        sut = hg.open_repository(self.repository_path)
        file_object = sut.get_file_contents("b.txt")
        self.assertEqual(file_object.read(), b"b")

    def test_get_object_at_revision(self):
        sut = hg.open_repository(self.repository_path)
        file_object = sut.get_file_contents("a.txt", revision=0)
        self.assertEqual(file_object.read(), b"a")

    def test_get_changeset(self):
        sut = hg.open_repository(self.repository_path)
        changeset = sut.get_changeset('0')
        self.assertEqual(
            changeset.changes, [
                change.Change(
                    sut, None, None, "a.txt", '0', change.ChangeType.add)])

    def test_get_modify_change(self):
        sut = hg.open_repository(self.repository_path)
        changeset = sut.get_changeset('1').changes
        self.assertEqual(changeset[0].action, change.ChangeType.modify)

    def test_get_copy_change(self):
        sut = hg.open_repository(self.repository_path)
        changeset = sut.get_changeset('2').changes
        self.assertEqual(changeset[0].action, change.ChangeType.copy)

    def test_get_rename_change(self):
        sut = hg.open_repository(self.repository_path)
        changeset = sut.get_changeset('3')
        changeset.optimize()
        self.assertEqual(changeset.changes[0].action, change.ChangeType.move)

    def test_get_remove_change(self):
        sut = hg.open_repository(self.repository_path)
        changeset = sut.get_changeset('4').changes
        self.assertEqual(changeset[0].action, change.ChangeType.remove)

    def test_get_derived_change(self):
        sut = hg.open_repository(self.repository_path)
        changeset = sut.get_changeset('5')
        changeset.optimize()
        self.assertEqual(
            changeset.changes[0].action,
            change.ChangeType.derived)

    def test_walk_history(self):
        sut = hg.open_repository(self.repository_path)
        self.assertEqual(len([x for x in sut.walk_history()]), 6)

if __name__ == '__main__':
    unittest.main()
