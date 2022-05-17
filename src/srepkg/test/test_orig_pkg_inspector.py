import pytest
from operator import attrgetter
from typing import NamedTuple
import srepkg.test.test_case_data as test_case_data
import src.srepkg.orig_pkg_inspector as opi


ErrorTest = NamedTuple(
    'ErrorTest', [('cfg_dir_name', str), ('expected_err', opi.PkgError)])


error_tests = [
    # ErrorTest(cfg_dir_name='non_existent_path',
    #           expected_err=opi.PkgError.PkgPathNotFound),
    # ErrorTest(cfg_dir_name='setup_cfg_missing',
    #           expected_err=opi.PkgError.NoSetupFilesFound),
    ErrorTest(cfg_dir_name='setup_cfg_empty',
              expected_err=opi.PkgError.PkgNameNotFound),
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


def sys_exit_condition(condition: ErrorTest):
    setup_cfg_dir = test_case_data.paths.setup_cfg_test_cases / condition.cfg_dir_name
    orig_pkg_inspector = opi.OrigPkgInspector(str(setup_cfg_dir))
    with pytest.raises(SystemExit) as e:
        orig_pkg_info = orig_pkg_inspector.get_orig_pkg_info()
    assert str(e.value) == condition.expected_err.msg


def test_sys_exit_conditions():
    for condition in error_tests:
        sys_exit_condition(condition)


def test_good_setup_cfg():
    setup_cfg_dir = test_case_data.paths.setup_cfg_test_cases / 'setup_cfg_valid'
    orig_pkg_inspector = opi.OrigPkgInspector(str(setup_cfg_dir))
    orig_pkg_info = orig_pkg_inspector.get_orig_pkg_info()

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
    setup_cfg_dir = test_case_data.paths.setup_cfg_test_cases /\
                    'setup_cfg_good_multi_dir_src_layout'
    orig_pkg_inspector = opi.OrigPkgInspector(str(setup_cfg_dir))
    orig_pkg_info = orig_pkg_inspector.get_orig_pkg_info()

    assert orig_pkg_info.package_dir_path == setup_cfg_dir / 'src'


def test_valid_pkg_with_cse():

    orig_pkg_info = opi.OrigPkgInspector(test_case_data.package_test_cases.t_proj_info.pkg_root) \
        .validate_orig_pkg_path() \
        .validate_setup_cfg() \
        .get_orig_pkg_info()

    assert orig_pkg_info.pkg_name == test_case_data.package_test_cases.t_proj_info.\
        pkg_name
    assert orig_pkg_info.root_path == test_case_data.package_test_cases.t_proj_info.\
        pkg_root
    assert orig_pkg_info.entry_pts.sort(key=attrgetter('command')) ==\
           test_case_data.package_test_cases.t_proj_info.cse_list.sort(
               key=attrgetter('command'))
