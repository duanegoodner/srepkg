import unittest
import shutil
from pathlib import Path
import srepkg.srepkg_builder as sb
import srepkg.test.test_path_calculator as tpc
import srepkg.test.test_case_data as test_case_data


class TestSrepkgBuilder(unittest.TestCase):
    orig_pkg_path = Path(__file__).parent.absolute() / 'test_case_data' / \
                    'package_test_cases' / 't_proj'
    srepkg_pkgs_non_temp_dir = Path(__file__).parent.absolute() / \
                               'test_case_data' / 'package_test_cases' / 'srepkg_pkgs'
    srepkg_dist_dir = Path(__file__).parent.absolute() / 'test_srepkg_dists'

    def setUp(self) -> None:
        if self.srepkg_pkgs_non_temp_dir.exists():
            shutil.rmtree(self.srepkg_pkgs_non_temp_dir)

        if self.srepkg_dist_dir.exists():
            shutil.rmtree(self.srepkg_dist_dir)

        self.builder_src_paths, self.builder_dest_paths = \
            tpc.calc_paths(
                [str(self.orig_pkg_path)])
        self.srepkg_builder = sb.SrepkgBuilder(
            tpc.calc_paths.locals['orig_pkg_info'],
            self.builder_src_paths, self.builder_dest_paths,
            self.srepkg_dist_dir)

    def tearDown(self) -> None:
        if self.srepkg_pkgs_non_temp_dir.exists():
            shutil.rmtree(self.srepkg_pkgs_non_temp_dir)

        if self.srepkg_dist_dir.exists():
            shutil.rmtree(self.srepkg_dist_dir)

    def test_srepkg_builder_paths(self) -> None:
        assert self.srepkg_builder.src_paths == self.builder_src_paths
        assert self.srepkg_builder.repkg_paths == self.builder_dest_paths

    def test_inner_pkg_copy(self) -> None:
        self.srepkg_builder.copy_inner_package()
        assert self.srepkg_builder.repkg_paths.root.exists()
        assert self.srepkg_builder.repkg_paths.srepkg.exists()
        assert self.srepkg_builder.repkg_paths.inner_setup_py.exists()
        assert self.srepkg_builder.repkg_paths.inner_setup_cfg.exists()

    def test_build_inner_layer(self) -> None:
        self.srepkg_builder.build_inner_layer()

        assert self.srepkg_builder.repkg_paths.inner_setup_py \
            .exists()
        assert self.srepkg_builder.repkg_paths.inner_setup_cfg \
            .exists()

    #  TODO add test that creates ...entry.py files & checks existence / content
    def test_build_mid_layer(self):
        self.srepkg_builder.build_inner_layer()
        self.srepkg_builder.build_mid_layer()

        assert self.srepkg_builder.repkg_paths.srepkg_control_components. \
            exists()
        assert self.srepkg_builder.repkg_paths.srepkg_entry_points.exists()
        assert self.srepkg_builder.repkg_paths.srepkg_init.exists()
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

    def test_build_srepkg(self):
        self.srepkg_builder.build_srepkg()


class TestSrepkgBuilderCustomDir(TestSrepkgBuilder):

    def setUp(self) -> None:
        if self.srepkg_pkgs_non_temp_dir.exists():
            shutil.rmtree(self.srepkg_pkgs_non_temp_dir)

        if self.srepkg_dist_dir.exists():
            shutil.rmtree(self.srepkg_dist_dir)

        self.builder_src_paths, self.builder_dest_paths = \
            tpc.calc_paths(
                [str(self.orig_pkg_path), '--srepkg_build_dir',
                 str(self.srepkg_pkgs_non_temp_dir)])
        self.srepkg_builder = sb.SrepkgBuilder(
            tpc.calc_paths.locals['orig_pkg_info'],
            self.builder_src_paths, self.builder_dest_paths,
            self.srepkg_dist_dir)

    # TODO add test to inspect contents of srepkg setup.cfg


class TestSrepkgBuilderNonSrcLayout(TestSrepkgBuilder, unittest.TestCase):
    orig_pkg_path = Path(__file__).parent.absolute() / 'test_case_data' / \
                    'package_test_cases' / 't_proj'
    srepkg_pkgs_non_temp_dir = Path(__file__).parent.absolute() / \
        'test_case_data' / 'package_test_cases' / 'srepkg_pkgs'
