import abc
import unittest
from pathlib import Path

import pytest


import srepkg.test.sfr_valid_cases.setup_file_test_case_data as sft
import srepkg.orig_pkg_inspector as pi
import srepkg.test.package_test_cases.expected_cfg_data as ecd

from srepkg.error_handling.error_messages import OrigPkgError


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
            ".cfg": sft.format_for_merge_and_opi_compare(
                getattr(sft, self.dataset_name)[".cfg"]),
            ".py": sft.format_for_merge_and_opi_compare(
                getattr(sft, self.dataset_name)[".py"]),
        }

    def setUp(self) -> None:
        self._src_code_inspector = pi.SrcCodeInspector(self.setup_dir)

    def test_get_orig_pkg_info(self):
        orig_pkg_info = self._src_code_inspector.get_orig_pkg_info()
        expected_merged_data = {
            **self.expected_data[".cfg"],
            **self.expected_data[".py"],
        }
        assert orig_pkg_info.pkg_name == expected_merged_data["name"]
        assert (
           sorted(orig_pkg_info.entry_pts,
                  key=lambda x: x.command) ==
           sorted(expected_merged_data["console_scripts"],
                  key=lambda x: x.command)
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

    def test_get_orig_pkg_info(self):
        with pytest.raises(SystemExit) as e:
            orig_pkg_info = self._src_code_inspector.get_orig_pkg_info()
        assert str(e.value) == OrigPkgError.SetupPyNotFound.msg


class TestOPIFullPkgTNonSrc(TestOPI):
    dataset_name = "tnonsrc"
    base_dir = Path(__file__).parent.absolute() / "package_test_cases"
    full_expected_data = getattr(ecd, dataset_name)
    expected_data = {
        ".cfg": sft.format_for_merge_and_opi_compare(full_expected_data[".cfg"]),
        ".py": sft.format_for_merge_and_opi_compare(full_expected_data[".py"]),
    }
