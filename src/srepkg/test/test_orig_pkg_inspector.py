import abc
import unittest

import pytest
from pathlib import Path
from typing import NamedTuple
import srepkg.orig_pkg_inspector as opi
import srepkg.test.sfr_valid_cases.sfr_expected_output as ev
import srepkg.test.package_test_cases.expected_cfg_data as ecd
from error_handling.error_messages import OrigPkgError

ErrorTest = NamedTuple(
    "ErrorTest", [("cfg_dir_name", str), ("expected_err", OrigPkgError)]
)

error_tests = [
    ErrorTest(
        cfg_dir_name="non_existent_path",
        expected_err=OrigPkgError.PkgPathNotFound,
    ),
    ErrorTest(
        cfg_dir_name="setup_cfg_missing",
        expected_err=OrigPkgError.NoSetupFilesFound,
    ),
    ErrorTest(
        cfg_dir_name="setup_cfg_empty",
        expected_err=OrigPkgError.PkgNameNotFound,
    ),
    ErrorTest(
        cfg_dir_name="setup_cfg_empty_sections",
        expected_err=OrigPkgError.PkgNameNotFound,
    ),
    ErrorTest(
        cfg_dir_name="setup_cfg_empty_values",
        expected_err=OrigPkgError.PkgNameNotFound,
    ),
    ErrorTest(cfg_dir_name="setup_cfg_no_cse", expected_err=OrigPkgError.NoCSE),
    ErrorTest(
        cfg_dir_name="setup_cfg_empty_cse", expected_err=OrigPkgError.NoCSE
    ),
]


# TODO replace Path(__file__)... references in tests with hardcoded paths


def sys_exit_condition(condition: ErrorTest):
    setup_cfg_dir = (
        Path(__file__).parent / "sfr_error_cases" / condition.cfg_dir_name
    )
    orig_pkg_inspector = opi.OrigPkgInspector(str(setup_cfg_dir))
    with pytest.raises(SystemExit) as e:
        orig_pkg_info = orig_pkg_inspector.get_orig_pkg_info()
    assert str(e.value) == condition.expected_err.msg


def test_sys_exit_conditions():
    for condition in error_tests:
        sys_exit_condition(condition)


class TestWarningConditions(unittest.TestCase):
    @property
    def base_dir(self):
        return Path(__file__).parent / "sfr_error_cases"

    @property
    @abc.abstractmethod
    def error_case_name(self):
        return "setup_cfg_wrong_format"

    @property
    def error_case_dir(self):
        return self.base_dir / self.error_case_name

    def setUp(self) -> None:
        self.orig_pkg_inspector = opi.OrigPkgInspector(str(self.error_case_dir))

    def test_warning_condition(self):
        with self.assertWarns(UserWarning) as tw:
            self.orig_pkg_inspector._get_all_setup_data()
        assert str(tw.warning) == OrigPkgError.SetupCfgReadError.msg


class TestOPI(unittest.TestCase):
    @property
    @abc.abstractmethod
    def dataset_name(self) -> str:
        return "match_non_src_layout"

    @property
    def base_dir(self):
        return Path(__file__).parent.absolute() / "sfr_valid_cases"

    @property
    def setup_dir(self):
        return self.base_dir / self.dataset_name

    @property
    def expected_data(self):
        return {
            ".cfg": ev.get_final_data(getattr(ev, self.dataset_name)[".cfg"]),
            ".py": ev.get_final_data(getattr(ev, self.dataset_name)[".py"]),
        }

    def setUp(self) -> None:
        self._orig_pkg_inspector = opi.OrigPkgInspector(str(self.setup_dir))

    def test_get_all_setup_data(self):
        self._orig_pkg_inspector._get_all_setup_data()
        assert (
            self._orig_pkg_inspector._all_setup_data["setup.cfg"]
            == self.expected_data[".cfg"]
        )
        assert (
            self._orig_pkg_inspector._all_setup_data["setup.py"]
            == self.expected_data[".py"]
        )

    def test_merge_all_setup_data(self):
        self._orig_pkg_inspector._get_all_setup_data()._merge_all_setup_data()

        assert self._orig_pkg_inspector._merged_data == {
            **self.expected_data[".cfg"],
            **self.expected_data[".py"],
        }

    def test_get_orig_pkg_info(self):
        orig_pkg_info = self._orig_pkg_inspector.get_orig_pkg_info()
        expected_merged_data = {
            **self.expected_data[".cfg"],
            **self.expected_data[".py"],
        }
        assert orig_pkg_info.pkg_name == expected_merged_data["name"]
        assert (
            orig_pkg_info.root_path == self._orig_pkg_inspector._orig_pkg_path
        )
        assert (
            orig_pkg_info.entry_pts == expected_merged_data["console_scripts"]
        )


class TestOPIMatchNonSrcLayout(TestOPI):
    dataset_name = "match_non_src_layout"


class TestOPIMatchSrcLayout(TestOPI):
    dataset_name = "match_src_layout"


class TestOPIMixedSrcLayoutValid(TestOPI):
    dataset_name = "mixed_src_layout_valid"


class TestOPISrcLayoutNoCfg(TestOPI):
    dataset_name = "src_layout_no_cfg"


class TestOPISrcLayoutNoPy(TestOPI):
    dataset_name = "src_layout_no_py"


class TestOPIFullPkgTNonSrc(TestOPI):
    dataset_name = "t_nonsrc"
    base_dir = Path(__file__).parent.absolute() / "package_test_cases"
    full_expected_data = getattr(ecd, dataset_name)
    expected_data = {
        ".cfg": ev.get_final_data(full_expected_data[".cfg"]),
        ".py": ev.get_final_data(full_expected_data[".py"]),
    }
