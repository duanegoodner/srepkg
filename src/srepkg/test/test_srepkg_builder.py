import unittest
import shutil
from pathlib import Path
import shared_data_structures.named_tuples as nt
import srepkg.srepkg_builder as sb
import srepkg.test.test_path_calculator as tpc


class TestSrepkgBuilder(unittest.TestCase):
    orig_pkg_path = (
        Path(__file__).parent.absolute() / "package_test_cases" / "t_proj"
    )
    srepkg_pkgs_non_temp_dir = (
        Path(__file__).parent.absolute() / "package_test_cases" / "srepkg_pkgs"
    )
    srepkg_dist_dir = Path(__file__).parent.absolute() / "test_srepkg_dists"

    def setUp(self) -> None:
        if self.srepkg_pkgs_non_temp_dir.exists():
            shutil.rmtree(self.srepkg_pkgs_non_temp_dir)

        if self.srepkg_dist_dir.exists():
            shutil.rmtree(self.srepkg_dist_dir)

        self.builder_src_paths, self.builder_dest_paths = tpc.calc_paths(
            [str(self.orig_pkg_path)]
        )

        task_builder_info = nt.TaskBuilderInfo(
            orig_pkg_info=tpc.calc_paths.locals["orig_pkg_info"],
            src_paths=self.builder_src_paths,
            repkg_paths=self.builder_dest_paths,
            dist_out_dir=self.srepkg_dist_dir
        )

        self.task_catalog_builder = sb.TaskCatalogBuilder(task_builder_info)
        task_catalog = self.task_catalog_builder.task_catalog
        self.task_order_arranger = sb.TaskOrderArranger(task_catalog)
        self.ordered_tasks = self.task_order_arranger.arrange_tasks()

    def tearDown(self) -> None:
        if self.srepkg_pkgs_non_temp_dir.exists():
            shutil.rmtree(self.srepkg_pkgs_non_temp_dir)

        if self.srepkg_dist_dir.exists():
            shutil.rmtree(self.srepkg_dist_dir)

    def test_srepkg_builder_paths(self) -> None:
        assert self.task_catalog_builder._info.src_paths == self.builder_src_paths
        assert self.task_catalog_builder._info.repkg_paths == self.builder_dest_paths

    def run_srepkg_builder_through_task(self, task_name: str, expected_path_id: str):
        end_index = self.task_order_arranger._task_order.index(task_name) + 1
        tasks = self.ordered_tasks[:end_index]
        srepkg_builder = sb.SrepkgBuilder(tasks)
        srepkg_builder.build_srepkg()

        expected_path = getattr(self.task_catalog_builder._info.repkg_paths, expected_path_id)
        assert expected_path.exists()

    def test_inner_pkg_copy(self) -> None:
        self.run_srepkg_builder_through_task(
            task_name='copy_inner_pkg', expected_path_id='srepkg')

    def test_create_srepkg_init(self) -> None:
        self.run_srepkg_builder_through_task(
            task_name='create_srepkg_init', expected_path_id='srepkg_init')

    def test_build_entry_pts(self):
        self.run_srepkg_builder_through_task(
            task_name='build_entry_pts', expected_path_id='srepkg_entry_points')

    def test_copy_entry_module(self):
        self.run_srepkg_builder_through_task(
            task_name='copy_entry_module', expected_path_id='entry_module')

    def test_build_srepkg_cfg(self):
        self.run_srepkg_builder_through_task(
            task_name='build_srepkg_cfg', expected_path_id='srepkg_setup_cfg')

    def test_build_inner_pkg_install_cfg(self):
        self.run_srepkg_builder_through_task(
            task_name='build_inner_pkg_install_cfg',
            expected_path_id='inner_pkg_install_cfg')

    def test_copy_inner_pkg_installer(self):
        self.run_srepkg_builder_through_task(
            task_name='copy_inner_pkg_installer',
            expected_path_id='inner_pkg_installer')

    def test_copy_srepkg_setup_py(self):
        self.run_srepkg_builder_through_task(
            task_name='copy_srepkg_setup_py',
            expected_path_id='srepkg_setup_py')

    def test_write_manifest(self):
        self.run_srepkg_builder_through_task(
            task_name='write_manifest', expected_path_id='manifest')

    def test_full_srepkg_build(self):
        srepkg_builder = sb.SrepkgBuilder(self.ordered_tasks)
        srepkg_builder.build_srepkg()
        zipfile_name = "-".join(
            [
                self.task_catalog_builder._info.repkg_paths.srepkg.name,
                self.task_catalog_builder._info.orig_pkg_info.version
            ]
        )

        assert (self.task_catalog_builder._info.dist_out_dir / (zipfile_name + '.zip')).exists()


class TestSrepkgBuilderCustomDir(TestSrepkgBuilder):
    def setUp(self) -> None:
        if self.srepkg_pkgs_non_temp_dir.exists():
            shutil.rmtree(self.srepkg_pkgs_non_temp_dir)

        if self.srepkg_dist_dir.exists():
            shutil.rmtree(self.srepkg_dist_dir)

        self.builder_src_paths, self.builder_dest_paths = tpc.calc_paths(
            [
                str(self.orig_pkg_path),
                "--construction_dir",
                str(self.srepkg_pkgs_non_temp_dir),
            ]
        )
        task_builder_info = nt.TaskBuilderInfo(
            orig_pkg_info=tpc.calc_paths.locals["orig_pkg_info"],
            src_paths=self.builder_src_paths,
            repkg_paths=self.builder_dest_paths,
            dist_out_dir=self.srepkg_dist_dir
        )

        self.task_catalog_builder = sb.TaskCatalogBuilder(task_builder_info)
        task_catalog = self.task_catalog_builder.task_catalog
        self.task_order_arranger = sb.TaskOrderArranger(task_catalog)
        self.ordered_tasks = self.task_order_arranger.arrange_tasks()

    # TODO add test to inspect contents of srepkg setup.cfg


class TestSrepkgBuilderNonSrcLayout(TestSrepkgBuilder, unittest.TestCase):
    orig_pkg_path = (
        Path(__file__).parent.absolute() / "package_test_cases" / "t_proj"
    )
    srepkg_pkgs_non_temp_dir = (
        Path(__file__).parent.absolute() / "package_test_cases" / "srepkg_pkgs"
    )
