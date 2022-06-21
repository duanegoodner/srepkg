import shutil
import unittest
from pathlib import Path
from typing import List
import srepkg.repackager as repackager


class TestRepackager(unittest.TestCase):

    _construction_dir = Path(__file__).parent.absolute() / 'test_srepkg_pkgs'
    _srepkg_dist_dir = Path(__file__).parent.absolute() / 'test_srepkg_dists'

    _orig_pkg_refs = ['howdoi', 'numpy', 'cowsay']

    def SetUp(self):
        if self._construction_dir.exists():
            shutil.rmtree(self._construction_dir)
        self._construction_dir.mkdir()

        if self._srepkg_dist_dir.exists():
            shutil.rmtree(self._srepkg_dist_dir)
        self._srepkg_dist_dir.mkdir()

    def tearDown(self) -> None:
        if self._construction_dir.exists():
            shutil.rmtree(self._construction_dir)

        if self._srepkg_dist_dir.exists():
            shutil.rmtree(self._srepkg_dist_dir)

    def run_single_pkg_test(self, orig_pkg_ref: str):
        my_repackager = repackager.Repackager(
            orig_pkg_ref, construction_dir=str(self._construction_dir),
            dist_out_dir=str(self._srepkg_dist_dir))
        my_repackager.repackage()

    def test_testproj(self):
        self.run_single_pkg_test('/Users/duane/dproj/testproj')

    def test_howdoi(self):
        self.run_single_pkg_test('howdoi')

    def test_cowsay(self):
        self.run_single_pkg_test('cowsay')

    def test_scrape(self):
        self.run_single_pkg_test('scrape')

    def test_flake8(self):
        self.run_single_pkg_test('flake8')




