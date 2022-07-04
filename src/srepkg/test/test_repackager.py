import shutil
import unittest
from pathlib import Path
import srepkg.repackager as repackager


class TestRepackager(unittest.TestCase):

    _construction_dir = Path(__file__).parent.absolute() / "test_srepkg_pkgs"
    _srepkg_dist_dir = Path(__file__).parent.absolute() / "test_srepkg_dists"
    # _orig_pkg_refs = ["howdoi", "numpy", "cowsay"]

    def setUp(self):
        if self._construction_dir.exists():
            shutil.rmtree(self._construction_dir)
        self._construction_dir.mkdir()

        if self._srepkg_dist_dir.exists():
            shutil.rmtree(self._srepkg_dist_dir)
        self._srepkg_dist_dir.mkdir()

        self.orig_cwd_content = list(Path.cwd().iterdir())

    def tearDown(self) -> None:
        if self._construction_dir.exists():
            shutil.rmtree(self._construction_dir)

        if self._srepkg_dist_dir.exists():
            shutil.rmtree(self._srepkg_dist_dir)

        curr_contents = list(Path.cwd().iterdir())
        for item in curr_contents:
            if item not in self.orig_cwd_content:
                item.unlink()

    @staticmethod
    def run_pkg_test_dirs_none(orig_pkg_ref: str):
        my_repackager = repackager.Repackager(
            orig_pkg_ref
        )
        my_repackager.repackage()

    def run_pkg_test_dirs_const(self, orig_pkg_ref: str):
        my_repackager = repackager.Repackager(
            orig_pkg_ref,
            construction_dir=str(self._construction_dir),
        )
        my_repackager.repackage()

    def run_pkg_test_dirs_dist(self, orig_pkg_ref: str):
        my_repackager = repackager.Repackager(
            orig_pkg_ref,
            dist_out_dir=str(self._srepkg_dist_dir),
        )
        my_repackager.repackage()

    def run_pkg_test_dirs_const_dist(self, orig_pkg_ref: str):
        my_repackager = repackager.Repackager(
            orig_pkg_ref,
            srepkg_name='dummy',
            construction_dir=str(self._construction_dir),
            dist_out_dir=str(self._srepkg_dist_dir),
        )
        my_repackager.repackage()

    def test_testproj_dirs_none(self):
        self.run_pkg_test_dirs_none("/Users/duane/dproj/testproj")

    def test_testproj_dirs_const(self):
        self.run_pkg_test_dirs_const("/Users/duane/dproj/testproj")

    def test_testproj_dirs_dist(self):
        self.run_pkg_test_dirs_dist("/Users/duane/dproj/testproj")

    def test_testproj_dirs_const_dist(self):
        self.run_pkg_test_dirs_const_dist("/Users/duane/dproj/testproj")

    def test_howdoi_pypi_dirs_none(self):
        self.run_pkg_test_dirs_none("howdoi")

    def test_howdoi_github_dirs_none(self):
        self.run_pkg_test_dirs_none(
            'git+https://github.com/gleitz/howdoi.git')

    # def test_howdoi_pypi_dirs_const(self):
    #     self.run_pkg_test_dirs_const("howdoi")
    #
    # def test_howdoi_pypi_dirs_dist(self):
    #     self.run_pkg_test_dirs_dist("howdoi")
    #
    # def test_howdoi_pypi_dirs_const_dist(self):
    #     self.run_pkg_test_dirs_const_dist("howdoi")

    # def test_howdoi_github_dirs_const(self):
    #     self.run_pkg_test_dirs_const(
    #         'git+https://github.com/gleitz/howdoi.git')
    #
    # def test_howdoi_github_dirs_dist(self):
    #     self.run_pkg_test_dirs_dist(
    #         'git+https://github.com/gleitz/howdoi.git')
    #
    # def test_howdoi_github_dirs_const_dist(self):
    #     self.run_pkg_test_dirs_const_dist(
    #         'git+https://github.com/gleitz/howdoi.git')

    # def test_cowsay_pypi(self):
    #     self.run_pkg_test_dirs_const_dist("cowsay")
    #
    # def test_scrape_pypi(self):
    #     self.run_pkg_test_dirs_const_dist("scrape")
    #
    # def test_flake8_pypi(self):
    #     self.run_pkg_test_dirs_const_dist("flake8")
