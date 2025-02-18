import shutil
import tempfile
from pathlib import Path
from test.shared_fixtures import sample_pkgs, tmp_construction_dir

import pytest

import srepkg.construction_dir as cdn
import srepkg.error_handling.custom_exceptions as ce
import srepkg.repackager_interfaces as rep_int
import srepkg.service_builder as sb
import srepkg.wheel_modifier as wm


class TestConstructionDirInit:

    @staticmethod
    def standard_init_tests(construction_dir: cdn.ConstructionDir):
        assert construction_dir.srepkg_root.exists()
        assert len(construction_dir.srepkg_root.name) == 32
        assert construction_dir.srepkg_root.parent == construction_dir._root
        assert construction_dir.srepkg_inner.exists()
        assert len(construction_dir.srepkg_inner.name) == 32
        assert (
            construction_dir.srepkg_inner.parent
            == construction_dir.srepkg_root
        )
        assert (
            construction_dir.supported_dist_types == cdn.DEFAULT_DIST_CLASSES
        )
        assert construction_dir._root_contents == [
            construction_dir.srepkg_root
        ]
        assert set(construction_dir._srepkg_root_contents) == {
            construction_dir.srepkg_inner,
            construction_dir.orig_pkg_dists,
        }
        assert construction_dir.srepkg_inner_contents == []
        assert construction_dir.pypi_version is None
        assert construction_dir.wheel_path is None

    def test_init_custom_construction_dir(self, tmp_path):
        construction_dir = cdn.CustomConstructionDir(
            construction_dir_command=tmp_path
        )
        self.standard_init_tests(construction_dir)
        assert construction_dir._root == tmp_path

    def test_init_temp_construction_dir(self):
        construction_dir = cdn.TempConstructionDir()
        self.standard_init_tests(construction_dir)
        assert construction_dir._temp_dir_obj is not None
        assert construction_dir._root == Path(
            construction_dir._temp_dir_obj.name
        )


class TestConstructionDirFinalize:

    @pytest.fixture(autouse=True)
    def _get_sample_pkgs(self, sample_pkgs):
        self._pkg_refs = sample_pkgs

    @pytest.mark.parametrize(
        "orig_pkg, srepkg_name, orig_pkg_name, num_dists",
        [
            ("testproj", None, "testproj", 1),
            ("testproj", "custom_name", "testproj", 1),
            ("testproj_targz", None, "testproj", 2),
        ],
    )
    def test_good_construction_dir_conditions(
        self, orig_pkg, srepkg_name, orig_pkg_name, num_dists
    ):
        srepkg_command = rep_int.SrepkgCommand(
            orig_pkg_ref=getattr(self._pkg_refs, orig_pkg),
            srepkg_name=srepkg_name,
        )
        service_builder = sb.ServiceBuilder(srepkg_command)
        osp = service_builder.create_orig_src_preparer()
        construction_dir_summary = osp.prepare()
        assert construction_dir_summary.pkg_name == orig_pkg_name
        assert len(construction_dir_summary.dists) == num_dists

    def test_get_dist_info_no_supported_dist_types(self):
        construction_dir = cdn.TempConstructionDir()
        construction_dir._supported_dist_types = []
        result = construction_dir._get_dist_info(self._pkg_refs.testproj)
        assert result is None

    def test_multiple_packages(self, sample_pkgs):
        service_builder = sb.ServiceBuilder(
            rep_int.SrepkgCommand(orig_pkg_ref=self._pkg_refs.testproj)
        )
        osp = service_builder.create_orig_src_preparer()
        construction_dir_summary = osp.prepare()
        shutil.copy2(
            src=sample_pkgs.wheel_inspect_whl,
            dst=construction_dir_summary.orig_pkg_dists,
        )

        with pytest.raises(ce.MultiplePackagesPresent):
            osp._receiver.finalize()

    def test_finalized_with_no_orig_pkg(self, tmp_construction_dir):
        with pytest.raises(ce.MissingOrigPkgContent):
            tmp_construction_dir.finalize()

    def test_sdist_to_wheel_converter_with_no_sdist(
        self, tmp_construction_dir
    ):
        converter = cdn.SdistToWheelConverter(tmp_construction_dir)
        with pytest.raises(ce.NoSDistForWheelConstruction):
            converter.build_wheel()


class TestConstructionDirSettle:

    def test_temp_cd_settle(self, tmp_construction_dir):
        tmp_construction_dir.settle()
        assert len(tmp_construction_dir.supported_dist_types) == 2

    def test_custom_cd_settle(self, tmp_path):
        custom_construction_dir = cdn.CustomConstructionDir(tmp_path)
        custom_construction_dir.settle()
        assert custom_construction_dir.srepkg_root.exists()


def test_with_hyphen_in_entry_point_name(tmp_construction_dir, sample_pkgs):
    construction_dir_command = Path(tempfile.TemporaryDirectory().name)
    construction_dir = cdn.CustomConstructionDir(
        construction_dir_command=construction_dir_command,
        srepkg_name_command=sample_pkgs.testprojhyphenentry_whl,
    )

    orig_wheel_path = Path(sample_pkgs.testprojhyphenentry_whl)
    wheel_name = orig_wheel_path.name

    test_wheel_path = construction_dir.orig_pkg_dists / wheel_name

    shutil.copy(
        src=orig_wheel_path,
        dst=test_wheel_path,
    )

    orig_dist_info = wm.WheelDistInfo(wheel_path=test_wheel_path)
    assert orig_dist_info.has_console_script_name_with_dash
    construction_dir._ensure_valid_console_script_names()
    assert not orig_dist_info.has_console_script_name_with_dash


# This test has long runtime but may be good edge-case check
# def test_numpy_sdist_to_wheel():
#     numpy_sdist_path = Path(
#         "/Users/duane/dproj/srepkg/src/srepkg/test/package_test_cases/"
#         "numpy-1.23.1.tar.gz")
#
#     cur_command = rep_int.SrepkgCommand(
#         orig_pkg_ref=str(numpy_sdist_path),
#         construction_dir="/Users/duane/srepkg_pkgs"
#     )
#
#     src_preparer = sb.ServiceBuilder(cur_command).create_orig_src_preparer()
#     src_preparer._retriever.retrieve()
#     src_preparer._provider.provide()
#
#     reviewer = cdn.ConstructionDirReviewer(src_preparer._receiver)
#     existing_dists_summary = reviewer.get_existing_dists_summary()
#     converter = cdn.SdistToWheelConverter(
#         construction_dir=src_preparer._receiver,
#         construction_dir_summary=existing_dists_summary
#     )
#
#     converter.build_wheel()
