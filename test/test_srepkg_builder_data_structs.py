import pkginfo
from pathlib import Path
from typing import Callable
import srepkg.repackager_data_structs as re_ds
from test.shared_fixtures import dummy_cdir_args


# These tests are not exhaustive. Just run conditions missed by other tests.
class TestSrepkgBuilderDataStructs:
    local_test_pkgs_path = (
        Path(__file__).parent.absolute() / "package_test_cases"
    )

    @staticmethod
    def mock_dist_info(
        dist_path: Path, dist_type: Callable[..., pkginfo.Distribution]
    ):
        dist_info = re_ds.DistInfo(
            path=dist_path, dist_obj=dist_type(str(dist_path))
        )
        return dist_info

    @staticmethod
    def run_all_property_getters(obj):
        property_getters = [
            item
            for item in dir(obj)
            if isinstance(getattr(type(obj), item, None), property)
        ]
        for getter in property_getters:
            getattr(obj, getter)

    def test_construction_dir_summary_init_with_dists(self, dummy_cdir_args):
        dist_info = self.mock_dist_info(
            dist_path=self.local_test_pkgs_path
            / "testproj-0.0.0-py3-none-any.whl",
            dist_type=pkginfo.Wheel,
        )
        construction_dir_summary = re_ds.ConstructionDirSummary(
            **dummy_cdir_args, dists=[dist_info]
        )
        assert len(construction_dir_summary.dists) == 1
        assert construction_dir_summary.has_platform_indep_wheel
        assert construction_dir_summary.has_wheel
        assert not construction_dir_summary.has_sdist
        assert (
            construction_dir_summary.src_for_srepkg_wheel.name
            == "testproj-0.0.0-py3-none-any.whl"
        )

    def test_construction_dir_summary_init_with_dists_and_entry_pts(
        self, dummy_cdir_args
    ):

        dist_info = self.mock_dist_info(
            dist_path=self.local_test_pkgs_path
            / "testproj-0.0.0-py3-none-any.whl",
            dist_type=pkginfo.Wheel,
        )
        entry_pt = re_ds.CSEntryPoint(
            command="test", module="test", attr="test"
        )
        construction_dir_summary = re_ds.ConstructionDirSummary(
            **dummy_cdir_args,
            dists=[dist_info],
            entry_pts=re_ds.PkgCSEntryPoints([entry_pt]),
        )
        assert len(construction_dir_summary.dists) == 1
        assert construction_dir_summary.has_platform_indep_wheel
        assert construction_dir_summary.has_wheel
        assert not construction_dir_summary.has_sdist
        assert (
            construction_dir_summary.src_for_srepkg_wheel.name
            == "testproj-0.0.0-py3-none-any.whl"
        )

    def test_wheel_path_getter_without_wheel(self, dummy_cdir_args):
        construction_dir_summary = re_ds.ConstructionDirSummary(
            **dummy_cdir_args
        )
        self.run_all_property_getters(construction_dir_summary)

    def test_sdist_path_getter_with_sdist(self, dummy_cdir_args):
        dist_info = self.mock_dist_info(
            dist_path=self.local_test_pkgs_path / "testproj-0.0.0.tar.gz",
            dist_type=pkginfo.SDist,
        )
        construction_dir_summary = re_ds.ConstructionDirSummary(
            **dummy_cdir_args, dists=[dist_info]
        )
        self.run_all_property_getters(construction_dir_summary)
