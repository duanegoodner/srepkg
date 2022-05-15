import unittest
import shutil
import srepkg.srepkg_builder as sb
import srepkg.test.test_path_calculator as tpc
import srepkg.test.test_case_data as test_case_data


class TestSrepkgBuilder(unittest.TestCase):
    srepkg_root = test_case_data.package_test_cases.t_proj_srepkg_info.srepkg_root
    orig_pkg_root = test_case_data.package_test_cases.t_proj_info.pkg_root

    def setUp(self) -> None:
        if self.srepkg_root.exists():
            shutil.rmtree(
                test_case_data.package_test_cases.t_proj_srepkg_info.srepkg_root)

        self.builder_src_paths, self.builder_dest_paths, \
            self.inner_pkg_src = tpc.calc_test_paths(
                self.orig_pkg_root)
        self.srepkg_builder = sb.SrepkgBuilder(
            tpc.calc_test_paths.locals['orig_pkg_info'],
            self.builder_src_paths, self.builder_dest_paths,
            self.inner_pkg_src)

    def tearDown(self) -> None:
        if test_case_data.package_test_cases.t_proj_srepkg_info.test_srepkg_pkgs_dir.\
                exists():
            shutil.rmtree(test_case_data.package_test_cases.t_proj_srepkg_info.
                          test_srepkg_pkgs_dir)

    def test_srepkg_builder_paths(self) -> None:
        assert self.srepkg_builder.src_paths == self.builder_src_paths
        assert self.srepkg_builder.repkg_paths == self.builder_dest_paths

    def test_inner_pkg_copy(self) -> None:
        self.srepkg_builder.copy_inner_package()
        assert self.srepkg_builder.repkg_paths.root.exists()
        assert self.srepkg_builder.repkg_paths.srepkg.exists()
        assert self.srepkg_builder.repkg_paths.inner_setup_py_active.exists()
        assert self.srepkg_builder.repkg_paths.inner_setup_cfg_active.exists()

    def test_build_inner_layer(self) -> None:
        self.srepkg_builder.build_inner_layer()

        assert not self.srepkg_builder.repkg_paths.inner_setup_py_active \
            .exists()
        assert (self.srepkg_builder.repkg_paths.inner_setup_cfg_active.parent /
                'setup_off.py').exists()
        assert not self.srepkg_builder.repkg_paths.inner_setup_cfg_active \
            .exists()
        assert (self.srepkg_builder.repkg_paths.inner_setup_cfg_active.parent /
                'setup_off.cfg').exists()

    #  TODO add test that creates ...entry.py files & checks existence / content
    def test_build_mid_layer(self):
        self.srepkg_builder.build_inner_layer()
        self.srepkg_builder.build_mid_layer()

        assert self.srepkg_builder.repkg_paths.srepkg_control_components.\
            exists()
        assert self.srepkg_builder.repkg_paths.srepkg_entry_points.exists()
        assert self.srepkg_builder.repkg_paths.srepkg_init.exists()
        assert self.srepkg_builder.repkg_paths.main_outer.exists()
        assert self.srepkg_builder.repkg_paths.pkg_names_mid.exists()

    def test_build_outer_layer(self):
        self.srepkg_builder.build_inner_layer()
        self.srepkg_builder.build_mid_layer()
        self.srepkg_builder.build_outer_layer()

        assert self.srepkg_builder.repkg_paths.srepkg_setup_cfg.exists()
        assert self.srepkg_builder.repkg_paths.inner_pkg_installer.exists()
        assert self.srepkg_builder.repkg_paths.srepkg_setup_py.exists()
        assert self.srepkg_builder.repkg_paths.pkg_names_outer.exists()
        assert self.srepkg_builder.repkg_paths.manifest.exists()


# TODO add test to inspect contents of srepkg setup.cfg


class TestSrepkgBuilderNonSrcLayout(TestSrepkgBuilder, unittest.TestCase):
    srepkg_root = test_case_data.package_test_cases.t_proj_srepkg_info.srepkg_root
    orig_pkg_root = test_case_data.package_test_cases.t_proj_info.\
        non_src_layout_pkg_root
