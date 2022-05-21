import abc
import unittest

import pytest
from operator import attrgetter
from pathlib import Path
from typing import NamedTuple
import srepkg.test.test_case_data as test_case_data
import src.srepkg.orig_pkg_inspector as opi
import src.srepkg.test.test_case_data.setup_files.sfr_expected_output as ev
import src.srepkg.setup_file_reader as sfr

ErrorTest = NamedTuple(
    'ErrorTest', [('cfg_dir_name', str), ('expected_err', opi.PkgError)])

error_tests = [
    ErrorTest(cfg_dir_name='non_existent_path',
              expected_err=opi.PkgError.PkgPathNotFound),
    ErrorTest(cfg_dir_name='empty_test',
              expected_err=opi.PkgError.NoSetupFilesFound),
    # ErrorTest(cfg_dir_name='setup_cfg_empty',
    #           expected_err=opi.PkgError.PkgNameNotFound),
    # ErrorTest(cfg_dir_name='setup_cfg_empty_sections',
    #           expected_err=opi.PkgError.PkgNameNotFound),
    # ErrorTest(cfg_dir_name='setup_cfg_empty_values',
    #           expected_err=opi.PkgError.InvalidPkgName),
    # ErrorTest(cfg_dir_name='setup_cfg_no_cse_no_main',
    #           expected_err=opi.PkgError.NoCommandLineAccess),
    # ErrorTest(cfg_dir_name='setup_cfg_empty_cse_no_main',
    #           expected_err=opi.PkgError.NoCommandLineAccess),
    # ErrorTest(cfg_dir_name='setup_cfg_wrong_format',
    #           expected_err=opi.PkgError.SetupCfgReadError),
    # ErrorTest(cfg_dir_name='setup_cfg_bad_package_dir',
    #           expected_err=opi.PkgError.InvalidPackageDirValue)
]


# TODO replace Path(__file__)... references in tests with hardcoded paths

def sys_exit_condition(condition: ErrorTest):
    # setup_cfg_dir =
    # test_case_data.paths.setup_cfg_test_cases / condition.cfg_dir_name
    setup_cfg_dir = Path(__file__).parent / 'test_case_data' / 'setup_files' / \
                    condition.cfg_dir_name
    orig_pkg_inspector = opi.OrigPkgInspector(str(setup_cfg_dir))
    with pytest.raises(SystemExit) as e:
        orig_pkg_info = orig_pkg_inspector._get_orig_pkg_info()
    assert str(e.value) == condition.expected_err.msg


def test_sys_exit_conditions():
    for condition in error_tests:
        sys_exit_condition(condition)


class OrigPackageInspector(unittest.TestCase):

    @property
    @abc.abstractmethod
    def dataset_name(self) -> str:
        return 'match_non_src_layout'

    @property
    def base_dir(self):
        return Path(__file__).parent.absolute() / 'test_case_data' / \
               'setup_files'

    @property
    def setup_dir(self):
        return self.base_dir / self.dataset_name

    @property
    def expected_data(self):
        return {
            sfr.SetupFileType.CFG: getattr(
                ev,
                self.dataset_name
            )[sfr.SetupFileType.CFG]['final_data'],
            sfr.SetupFileType.PY: getattr(
                ev,
                self.dataset_name
            )[sfr.SetupFileType.PY]['final_data']
        }

    def setUp(self) -> None:
        self._orig_pkg_inspector = opi.OrigPkgInspector(str(self.setup_dir))

    def test_get_orig_pkg_info(self):
        self._orig_pkg_inspector._get_orig_pkg_info()
        assert self._orig_pkg_inspector._all_setup_file_info['setup.cfg'] ==\
               sfr.SetupFileInfo(**self.expected_data[sfr.SetupFileType.CFG])
        assert self._orig_pkg_inspector._all_setup_file_info['setup.py'] ==\
               sfr.SetupFileInfo(**self.expected_data[sfr.SetupFileType.PY])





# class OrigPackageInspector(unittest.TestCase):
#     base_path = Path(__file__).parent.absolute() / 'test_case_data' / \
#                 'setup_files'
#
#     test_case_data = [
#         # ('file_type_only', ev.file_type_only_py, ev.file_type_only_cfg),
#         ('match_src_layout', ev.match_src_layout_py, ev.match_src_layout_cfg),
#         ('match_non_src_layout', ev.match_non_src_layout_py,
#          ev.match_non_src_layout_cfg),
#         ('src_layout_no_cfg', ev.src_layout_no_cfg_py,
#          ev.src_layout_no_cfg_cfg),
#         ('src_layout_no_py', ev.src_layout_no_py_py, ev.src_layout_no_py_cfg)
#     ]
#
#     def run_test(self, setup_dir_rel_path: str, py_data: dict, cfg_data: dict):
#         pkg_inspector = opi.OrigPkgInspector(
#             str(self.base_path / setup_dir_rel_path))
#         pkg_inspector._get_orig_pkg_info()
#         assert pkg_inspector._all_setup_file_info['setup.cfg'] ==\
#                sfr.SetupFileInfo(**cfg_data['final_data'])
#         assert pkg_inspector._all_setup_file_info['setup.py'] ==\
#                sfr.SetupFileInfo(**py_data['final_data'])
#
#     def test_all_cases(self):
#         for test_case in self.test_case_data:
#             self.run_test(test_case[0], test_case[1], test_case[2])


def test_good_setup_cfg():
    setup_cfg_dir = test_case_data.paths.setup_cfg_test_cases / 'setup_cfg_valid'
    orig_pkg_inspector = opi.OrigPkgInspector(str(setup_cfg_dir))
    orig_pkg_info = orig_pkg_inspector._get_orig_pkg_info()

    actual_pkg_data = test_case_data.setup_cfg_test_cases.setup_cfg_valid.cfg_data

    assert orig_pkg_info.root_path == setup_cfg_dir
    assert orig_pkg_info.pkg_name == actual_pkg_data.pkg_name
    assert orig_pkg_info.entry_pts == actual_pkg_data.entry_pts


def test_no_cse_with_main():
    setup_cfg_dir = test_case_data.paths.setup_cfg_test_cases / 'setup_cfg_valid'
    orig_pkg_inspector = opi.OrigPkgInspector(str(setup_cfg_dir))
    orig_pkg_info = orig_pkg_inspector.get_orig_pkg_info()

    actual_pkg_data = test_case_data.setup_cfg_test_cases.setup_cfg_valid.cfg_data

    assert orig_pkg_info.root_path == setup_cfg_dir
    assert orig_pkg_info.pkg_name == actual_pkg_data.pkg_name


def test_src_layout_multi_dir():
    setup_cfg_dir = test_case_data.paths.setup_cfg_test_cases / \
                    'setup_cfg_good_multi_dir_src_layout'
    orig_pkg_inspector = opi.OrigPkgInspector(str(setup_cfg_dir))
    orig_pkg_info = orig_pkg_inspector.get_orig_pkg_info()

    assert orig_pkg_info.package_dir_path == setup_cfg_dir / 'src'


def test_valid_pkg_with_cse():
    orig_pkg_info = opi.OrigPkgInspector(
        test_case_data.package_test_cases.t_proj_info.pkg_root) \
        .validate_orig_pkg_path() \
        .validate_setup_cfg() \
        .get_orig_pkg_info()

    assert orig_pkg_info.pkg_name == test_case_data.package_test_cases.t_proj_info. \
        pkg_name
    assert orig_pkg_info.root_path == test_case_data.package_test_cases.t_proj_info. \
        pkg_root
    assert orig_pkg_info.entry_pts.sort(key=attrgetter('command')) == \
           test_case_data.package_test_cases.t_proj_info.cse_list.sort(
               key=attrgetter('command'))
