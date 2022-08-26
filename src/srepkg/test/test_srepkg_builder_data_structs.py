import pkginfo
from pathlib import Path
from typing import Callable

# import srepkg.srepkg_builder_data_structs as sb_ds
import srepkg.repackager_data_structs as re_ds


# These tests are not exhaustive. Just run conditions missed by other tests.
class TestSrepkgBuilderDataStructs:
    local_test_pkgs_path = Path(__file__).parent.absolute() / \
                           "package_test_cases"

    @staticmethod
    def mock_dist_info(dist_path: Path,
                       dist_type: Callable[..., pkginfo.Distribution]):
        dist_info = re_ds.DistInfo(
            path=dist_path,
            dist_obj=dist_type(str(dist_path)))

        return dist_info

    @staticmethod
    def run_all_property_getters(obj):
        property_getters = [item for item in dir(obj) if isinstance(
            getattr(type(obj), item, None), property)]
        for getter in property_getters:
            getattr(obj, getter)

    def test_construction_dir_summary_init_with_dists(self):
        dist_info = self.mock_dist_info(
            dist_path=self.local_test_pkgs_path /
            "testproj-0.0.0-py3-none-any.whl",
            dist_type=pkginfo.Wheel)

        return re_ds.ConstructionDirSummary(
            pkg_name="testproj",
            pkg_version="1.0.0",
            srepkg_name="dummy",
            srepkg_root=Path("dummy"),
            orig_pkg_dists=Path("dummy"),
            srepkg_inner=Path("dummy"),
            dists=[dist_info],
        )

    def test_construction_dir_summary_init_with_dists_and_entry_pts(self):
        dist_info = self.mock_dist_info(
            dist_path=self.local_test_pkgs_path /
            "testproj-0.0.0-py3-none-any.whl",
            dist_type=pkginfo.Wheel)

        entry_pt = re_ds.CSEntryPoint(
            command="test", module="test", attr="test")

        return re_ds.ConstructionDirSummary(
            pkg_name="testproj",
            pkg_version="1.0.0",
            srepkg_name="dummy",
            srepkg_root=Path("dummy"),
            orig_pkg_dists=Path("dummy"),
            srepkg_inner=Path("dummy"),
            dists=[dist_info],
            entry_pts=re_ds.PkgCSEntryPoints([entry_pt]))

    def test_wheel_path_getter_without_wheel(self):
        construction_dir_summary = re_ds.ConstructionDirSummary(
            pkg_name="test_proj",
            pkg_version="1.0.0",
            srepkg_name="dummy",
            srepkg_root=Path("dummy"),
            orig_pkg_dists=Path("dummy"),
            srepkg_inner=Path("dummy"),
        )
        self.run_all_property_getters(construction_dir_summary)
        # return construction_dir_summary.wheel_path

    def test_sdist_path_getter_with_sdist(self):
        dist_info = self.mock_dist_info(
            dist_path=self.local_test_pkgs_path / "testproj-0.0.0.tar.gz",
            dist_type=pkginfo.SDist)
        construction_dir_summary = re_ds.ConstructionDirSummary(
            pkg_name="testproj",
            pkg_version="1.0.0",
            srepkg_name="dummy",
            srepkg_root=Path("dummy"),
            orig_pkg_dists=Path("dummy"),
            srepkg_inner=Path("dummy"),
            dists=[dist_info])
        self.run_all_property_getters(construction_dir_summary)
