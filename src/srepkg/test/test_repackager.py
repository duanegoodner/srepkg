import shutil
import unittest
from pathlib import Path
from typing import List
import srepkg.repackager as repackager


class TestRepackager(unittest.TestCase):

    _srepkg_location = Path(__file__).parent.absolute() / 'test_srepkg_pkgs'

    _pkg_refs = ['howdoi', 'numpy', 'cowsay']

    def SetUp(self):
        if self._srepkg_location.exists():
            shutil.rmtree(self._srepkg_location)
        self._srepkg_location.mkdir()

    def tearDown(self) -> None:
        if self._srepkg_location.exists():
            shutil.rmtree(self._srepkg_location)

    def run_single_pkg_test(self, pkg_ref: str):
        my_repackager = repackager.Repackager(
            pkg_ref, srepkg_location=self._srepkg_location)
        my_repackager.repackage()

    def test_testproj(self):
        self.run_single_pkg_test('/Users/duane/dproj/testproj')

    def test_howdoi(self):
        self.run_single_pkg_test('howdoi')

    def test_numpy(self):
        self.run_single_pkg_test('numpy')

    def test_cowsay(self):
        self.run_single_pkg_test('cowsay')

    # def test_pandas(self):
    #     self.run_single_pkg_test('pandas')

    def test_requests(self):
        self.run_single_pkg_test('requests')

    def test_scrape(self):
        self.run_single_pkg_test('scrape')

    def test_mechanize(self):
        self.run_single_pkg_test('mechanize')

    def test_pyquery(self):
        self.run_single_pkg_test('pyquery')

    def test_mypy(self):
        self.run_single_pkg_test('mypy')

    def test_flake8(self):
        self.run_single_pkg_test('flake8')

    def test_black(self):
        self.run_single_pkg_test('black')









#
# def test_howdoi_pypi():
#     my_repackager = repackager.Repackager('howdoi', 'howdoipypi')
#     my_repackager.repackage()
#
#
# def test_howdoi_local():
#     my_repackager = repackager.Repackager(
#         '/Users/duane/srepkg_temp_dirs/howdoi/howdoi-2.0.19', 'howdoilocal')
#     my_repackager.repackage()
#
#
# def test_howdoi_local_default_name():
#     my_repackager = repackager.Repackager(
#         '/Users/duane/srepkg_temp_dirs/howdoi/howdoi-2.0.19')
#     my_repackager.repackage()
#
#
# def test_howdoi_github():
#     my_repackager = repackager.Repackager(
#         'git+https://github.com/gleitz/howdoi',
#         'howdoigithub')
#     my_repackager.repackage()




