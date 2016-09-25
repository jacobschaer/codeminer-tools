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
        cls.server_path = tempfile.mkdtemp()
        cls.repository_root = tempfile.mkdtemp()
        cls.repository_path = os.path.join(cls.repository_root, 'test_repo')
        run_shell_command('svnadmin create test_repo', cwd=cls.server_path)
        cls.server = run_shell_command('svnserve -d --foreground -r {path}'.format(
                                       path=cls.server_path), wait=False)
        run_shell_command('svn co svn://127.0.0.1/test_repo', cwd=cls.repository_root)
    
    @classmethod
    def tearDownClass(cls):
        pass
        cls.server.kill()
        shutil.rmtree(cls.server_path)
        shutil.rmtree(cls.repository_root)

    def test_get_info(self):
        sut = svn.open_repository(self.repository_path)
        info = sut.info()
        print(info)
        self.assertEqual(info['url'], 'svn://127.0.0.1/test_repo')
        self.assertEqual(info['repository']['root'], 'svn://127.0.0.1/test_repo')
        self.assertEqual(info['wc-info']['wcroot-abspath'], sut.path)
        self.assertTrue(int(info['commit']['@revision']) >= 0)

    def test_get_add_files(self):
        test_file = os.path.join(self.repository_path, 'a.txt')
        with open(test_file, 'w') as test_file:
            test_file.write('a')
        run_shell_command('svn add a.txt', cwd=self.repository_path)
        run_shell_command('svn commit -m "Test"')
        sut = svn.open_repository(self.repository_path)
        revision = sut.info()['commit']['@revision']
        commit = sut.get_changes(revision)
        print(commit)

if __name__ == '__main__':
    unittest.main()