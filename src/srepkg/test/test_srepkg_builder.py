import unittest
import shutil
import srepkg.test.calc_test_paths as ctp
import srepkg.srepkg_builder as sb
import srepkg.test.t_proj_srepkg_info as tpsi


class TestSrepkgBuilder(unittest.TestCase):

    def setUp(self) -> None:
        if tpsi.srepkg_root.exists():
            shutil.rmtree(tpsi.srepkg_root)

        self.builder_src_paths, self.builder_dest_paths = ctp.calc_test_paths()

        self.srepkg_builder = sb.SrepkgBuilder(
            ctp.calc_test_paths.locals['orig_pkg_info'],
            self.builder_src_paths, self.builder_dest_paths)

    def tearDown(self) -> None:
        if tpsi.test_srepkg_pkgs_dir.exists():
            shutil.rmtree(tpsi.test_srepkg_pkgs_dir)

    def test_srepkg_builder_paths(self):
        assert self.srepkg_builder.src_paths == self.builder_src_paths
        assert self.srepkg_builder.repkg_paths == self.builder_dest_paths

    def test_inner_pkg_copy(self):
        self.srepkg_builder.copy_inner_package()
        assert self.srepkg_builder.repkg_paths.root.exists()
        assert self.srepkg_builder.repkg_paths.srepkg.exists()
        assert self.srepkg_builder.repkg_paths.inner_setup_py_active.exists()
        assert self.srepkg_builder.repkg_paths.inner_setup_cfg_active.exists()

    def test_modify_inner_pkg(self):
        self.srepkg_builder.copy_inner_package()
        self.srepkg_builder.inner_pkg_install_inhibit()

        assert not self.srepkg_builder.repkg_paths.inner_setup_py_active.exists()
        assert (self.srepkg_builder.repkg_paths.inner_setup_cfg_active.parent /
                'setup_off.py').exists()
        assert not self.srepkg_builder.repkg_paths.inner_setup_cfg_active.exists()
        assert (self.srepkg_builder.repkg_paths.inner_setup_cfg_active.parent /
                'setup_off.cfg').exists()




