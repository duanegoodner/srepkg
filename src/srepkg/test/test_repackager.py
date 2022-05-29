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

    def test_howdoi(self):
        self.run_single_pkg_test('howdoi')

    def test_numpy(self):
        self.run_single_pkg_test('numpy')

    def test_cowsay(self):
        self.run_single_pkg_test('cowsay')


#
# my_pkg_refs = ['howdoi', 'numpy', 'cowsay']
# my_srepkg_location = Path(__file__).parent.absolute() / 'test_srepkg_pkgs'
#
#
# def run_single_test(pkg_ref: str, srepkg_location: Path):
#     if srepkg_location.exists():
#         shutil.rmtree(srepkg_location)
#
#     my_repackager = repackager.Repackager(
#         pkg_ref=pkg_ref, srepkg_location=srepkg_location)
#     my_repackager.repackage()
#
#     if srepkg_location.exists():
#         shutil.rmtree(srepkg_location)
#
#
# def test_multiple_packages():
#     for pkg in my_pkg_refs:
#         run_single_test(pkg_ref=pkg, srepkg_location=my_srepkg_location)







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




