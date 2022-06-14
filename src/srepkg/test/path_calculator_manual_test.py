import shutil
import tempfile
import unittest
from pathlib import Path
from typing import List
import srepkg.command_input as ci
import srepkg.orig_pkg_inspector as opi
import srepkg.path_calculator as pc
import srepkg.repackager as re
import srepkg.test.test_case_data as test_case_data
import srepkg.test.t_utils as tu

repackaging_components = test_case_data.paths.repackaging_components_actual


@tu.p_loc.PersistentLocals
def calc_test_paths_2(user_args: List[str]):
    ci_args = ci.get_args(user_args)
    orig_pkg_info = opi.OrigPkgInspector(ci_args.pkg_ref).get_orig_pkg_info()

    srepkg_temp_dir = None

    if ci_args.srepkg_build_dir:
        srepkg_build_dir = Path(ci_args.srepkg_build_dir)
    else:
        srepkg_temp_dir = tempfile.TemporaryDirectory()
        srepkg_build_dir = Path(srepkg_temp_dir.name)

    builder_paths_calculator = pc.BuilderPathsCalculator(
        orig_pkg_info=orig_pkg_info,
        srepkg_build_dir=srepkg_build_dir,
        srepkg_custom_name=ci_args.srepkg_name)

    builder_src_paths, builder_dest_paths = \
        builder_paths_calculator.calc_builder_paths()

    if srepkg_temp_dir:
        srepkg_temp_dir.cleanup()

    return builder_src_paths, builder_dest_paths


t_proj_root = Path(__file__).parent / 'test_case_data' / 'package_test_cases' / \
              't_proj'

t_projsrepkg_root = Path(__file__).parent / 'test_case_data' / \
                    'package_test_cases' / 'test_srepkg_pkgs'

calc_test_paths_2([str(t_proj_root), '--srepkg_build_dir', str(t_projsrepkg_root)])
print(calc_test_paths_2.locals)
