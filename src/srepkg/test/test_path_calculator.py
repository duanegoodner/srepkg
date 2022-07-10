import shutil
import tempfile
import unittest
from pathlib import Path

import pytest

import srepkg.command_input as ci
import srepkg.orig_pkg_inspector as pi
import srepkg.path_calculator as pc
import srepkg.test.t_utils as tu

repackaging_components = (
    Path(__file__).parent.parent.absolute() / "repackaging_components"
)


@tu.p_loc.PersistentLocals
def calc_paths(ci_args):
    args = ci.get_args(ci_args)
    orig_pkg_info = pi.SrcCodeInspector(args.orig_pkg_ref).get_orig_pkg_info()

    srepkg_temp_dir = None

    if not args.construction_dir:
        srepkg_temp_dir = tempfile.TemporaryDirectory()
        construction_dir = Path(srepkg_temp_dir.name)
    else:
        construction_dir = Path(args.construction_dir)

    builder_paths_calculator = pc.SrepkgBuilderPathsCalculator(
        orig_pkg_name=orig_pkg_info.pkg_name,
        construction_dir=construction_dir,
        srepkg_custom_name=args.srepkg_name,
    )

    # these local vars not needed to reach return value. defining here so
    # they can be accessed as PersistentLocals data members in test functs
    final_srepkg_name = builder_paths_calculator._srepkg_name
    srepkg_root = builder_paths_calculator._srepkg_root

    (
        builder_src_paths,
        builder_dest_paths,
    ) = builder_paths_calculator.calc_builder_paths()

    if srepkg_temp_dir:
        srepkg_temp_dir.cleanup()

    return builder_src_paths, builder_dest_paths


class TestPathCalc(unittest.TestCase):
    orig_pkg_path = (
        Path(__file__).parent.absolute() / "package_test_cases" / "tproj"
    )
    srepkg_pkgs_non_temp_dir = (
        Path(__file__).parent.absolute() / "package_test_cases" / "srepkg_pkgs"
    )

    def setUp(self) -> None:
        if self.srepkg_pkgs_non_temp_dir.exists():
            shutil.rmtree(self.srepkg_pkgs_non_temp_dir)

        self.builder_src_paths, self.builder_dest_paths = calc_paths(
            [str(self.orig_pkg_path)]
        )

    def test_builder_src_paths(self):
        builder_src_paths = calc_paths.locals["builder_src_paths"]
        assert (
            builder_src_paths.entry_module
            == repackaging_components
            / "mid_layer"
            / "entry_point_runner.py"
        )
        assert (
            builder_src_paths.entry_point_template
            == repackaging_components / "mid_layer" / "generic_entry.py"
        )
        assert (
            builder_src_paths.srepkg_setup_py
            == repackaging_components / "outer_layer" / "srepkg_setup.py"
        )
        assert (
            builder_src_paths.srepkg_setup_cfg
            == repackaging_components
            / "outer_layer"
            / "srepkg_starter_setup.cfg"
        )

    def test_builder_dest_paths(self):
        builder_dest_paths = calc_paths.locals["builder_dest_paths"]
        srepkg_root = calc_paths.locals["srepkg_root"]

        srepkg_content_path = srepkg_root / calc_paths.locals["final_srepkg_name"]
        srepkg_entry_points = srepkg_content_path / "srepkg_entry_points"
        srepkg_entry_module = srepkg_entry_points / "entry_point_runner.py"
        srepkg_setup_cfg = srepkg_root / "setup.cfg"
        srepkg_setup_py = srepkg_root / "setup.py"
        srepkg_init = srepkg_content_path / "__init__.py"

        assert builder_dest_paths.srepkg == srepkg_content_path
        assert builder_dest_paths.entry_module == srepkg_entry_module
        assert builder_dest_paths.srepkg_entry_points == srepkg_entry_points
        assert builder_dest_paths.srepkg_setup_cfg == srepkg_setup_cfg
        assert builder_dest_paths.srepkg_setup_py == srepkg_setup_py
        assert builder_dest_paths.srepkg_init == srepkg_init


class TestPathCalcCustomDir(TestPathCalc):
    def setUp(self) -> None:
        if self.srepkg_pkgs_non_temp_dir.exists():
            shutil.rmtree(self.srepkg_pkgs_non_temp_dir)

        self.builder_src_paths, self.builder_dest_paths = calc_paths(
            [
                str(self.orig_pkg_path),
                "--construction_dir",
                str(self.srepkg_pkgs_non_temp_dir),
            ]
        )


class TestPathCalcCustomDirAndPkgName(TestPathCalc):
    def setUp(self) -> None:
        if self.srepkg_pkgs_non_temp_dir.exists():
            shutil.rmtree(self.srepkg_pkgs_non_temp_dir)

        self.builder_src_paths, self.builder_dest_paths = calc_paths(
            [
                str(self.orig_pkg_path),
                "--construction_dir",
                str(self.srepkg_pkgs_non_temp_dir),
                "--srepkg_name",
                "custom_name",
            ]
        )


def test_srepkg_root_already_exists():
    orig_pkg_path = (
            Path(__file__).parent.absolute() / "package_test_cases" / "tproj"
    )

    srepkg_pkgs_non_temp_dir = (
            Path(
                __file__).parent.absolute() / "package_test_cases"
    )

    with pytest.raises(SystemExit) as e:
        builder_src_paths, builder_dest_paths = calc_paths([
            str(orig_pkg_path), '--construction_dir', str(srepkg_pkgs_non_temp_dir)
        ])
    assert str(e.value) ==\
           f"Destination path " \
           f"{srepkg_pkgs_non_temp_dir / 'tproj_as_tprojsrepkg'} "\
           f"already exists"

