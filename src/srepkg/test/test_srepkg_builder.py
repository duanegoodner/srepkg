import unittest
import shutil
import srepkg.srepkg_builder as sb
import srepkg.test.test_path_calculator as tpc
import srepkg.test.t_data as t_data


class TestSrepkgBuilder(unittest.TestCase):

    def setUp(self) -> None:
        if t_data.t_proj_srepkg_info.srepkg_root.exists():
            shutil.rmtree(t_data.t_proj_srepkg_info.srepkg_root)

        self.builder_src_paths, self.builder_dest_paths = tpc.calc_test_paths()

        self.srepkg_builder = sb.SrepkgBuilder(
            tpc.calc_test_paths.locals['orig_pkg_info'],
            self.builder_src_paths, self.builder_dest_paths)

    def tearDown(self) -> None:
        if t_data.t_proj_srepkg_info.test_srepkg_pkgs_dir.exists():
            shutil.rmtree(t_data.t_proj_srepkg_info.test_srepkg_pkgs_dir)

    def test_srepkg_builder_paths(self) -> None:
        assert self.srepkg_builder.src_paths == self.builder_src_paths
        assert self.srepkg_builder.repkg_paths == self.builder_dest_paths

    def test_inner_pkg_copy(self) -> None:
        self.srepkg_builder.copy_inner_package()
        assert self.srepkg_builder.repkg_paths.root.exists()
        assert self.srepkg_builder.repkg_paths.srepkg.exists()
        assert self.srepkg_builder.repkg_paths.inner_setup_py_active.exists()
        assert self.srepkg_builder.repkg_paths.inner_setup_cfg_active.exists()

    def test_inner_pkg_setup_off(self) -> None:
        self.srepkg_builder.copy_inner_package()
        self.srepkg_builder.inner_pkg_setup_off()

        assert not self.srepkg_builder.repkg_paths.inner_setup_py_active.exists()
        assert (self.srepkg_builder.repkg_paths.inner_setup_cfg_active.parent /
                'setup_off.py').exists()
        assert not self.srepkg_builder.repkg_paths.inner_setup_cfg_active.exists()
        assert (self.srepkg_builder.repkg_paths.inner_setup_cfg_active.parent /
                'setup_off.cfg').exists()

    # TODO modify this test to inspect contents of srepkg setup.cfg
    def test_build_sr_cfg(self) -> None:
        self.srepkg_builder.copy_inner_package()
        self.srepkg_builder.inner_pkg_setup_off()
        self.srepkg_builder.build_sr_cfg()

        assert self.srepkg_builder.repkg_paths.srepkg_setup_cfg.exists()

    def test_entry_points_init(self) -> None:
        self.srepkg_builder.copy_inner_package()
        self.srepkg_builder.inner_pkg_setup_off()
        self.srepkg_builder.build_sr_cfg()
        self.srepkg_builder.repkg_paths.srepkg_entry_points.mkdir()
        self.srepkg_builder.write_entry_point_init()

        assert self.srepkg_builder.repkg_paths.srepkg_entry_points_init.exists()

    #  TODO add test that creates ...entry.py files & checks existence / content

    def test_build_srepkg_dash_m(self) -> None:
        self.srepkg_builder.build_srepkg()

        assert self.srepkg_builder.repkg_paths.main_inner.exists() ==\
               self.srepkg_builder.repkg_paths.main_inner_orig.exists()















