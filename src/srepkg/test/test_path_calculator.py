import shutil
import unittest
from pathlib import Path
import srepkg.command_input as ci
import srepkg.orig_pkg_inspector as opi
import srepkg.path_calculator as pc
import srepkg.test.t_data as t_data
import srepkg.test.t_utils as tu


repackaging_components = t_data.paths.repackaging_components_actual


@tu.p_loc.PersistentLocals
def calc_test_paths(pkg_root: Path = t_data.t_proj_info.pkg_root):
    args = ci.get_args([str(pkg_root)])

    orig_pkg_info = opi.OrigPkgInspector(args.orig_pkg_path) \
        .validate_orig_pkg_path() \
        .validate_setup_cfg() \
        .get_orig_pkg_info()

    builder_paths_calculator = pc.BuilderPathsCalculator(
        orig_pkg_info, args.srepkg_name)

    # use non-standard path for srepkgs_pkgs to avoid unwanted overwrite
    builder_paths_calculator.srepkg_pkgs_dir =\
        t_data.t_proj_srepkg_info.test_srepkg_pkgs_dir

    builder_src_paths, builder_dest_paths =\
        builder_paths_calculator.calc_builder_paths()

    return builder_src_paths, builder_dest_paths


class TestPathCalculator(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        if t_data.t_proj_srepkg_info.srepkg_root.exists():
            shutil.rmtree(t_data.t_proj_srepkg_info.srepkg_root)

        calc_test_paths()

    def test_confirm_calc_paths_locals_accessible(self):
        print(calc_test_paths.locals)

    def test_builder_src_paths(self):
        builder_src_paths = calc_test_paths.locals['builder_src_paths']
        assert builder_src_paths.srepkg_init == repackaging_components / \
               'srepkg_init.py'
        assert builder_src_paths.entry_module == repackaging_components / \
               'srepkg_control_components' / 'entry_points.py'
        assert builder_src_paths.entry_point_template == \
               repackaging_components / 'generic_entry.py'
        assert builder_src_paths.srepkg_control_components == \
               repackaging_components / 'srepkg_control_components'
        assert builder_src_paths.srepkg_setup_py == repackaging_components / \
               'srepkg_setup.py'
        assert builder_src_paths.srepkg_setup_cfg == repackaging_components / \
               'srepkg_starter_setup.cfg'

    def test_builder_dest_paths(self):
        builder_dest_paths = calc_test_paths.locals['builder_dest_paths']

        srepkg_path = t_data.t_proj_srepkg_info.srepkg_root / \
                      ('t_proj' + 'srepkg')
        srepkg_control_components = srepkg_path / 'srepkg_control_components'
        srepkg_entry_module = srepkg_control_components / 'entry_points.py'
        srepkg_entry_points = srepkg_path / 'srepkg_entry_points'
        srepkg_setup_cfg = t_data.t_proj_srepkg_info.srepkg_root / 'setup.cfg'
        srepkg_setup_py = t_data.t_proj_srepkg_info.srepkg_root / 'setup.py'
        srepkg_init = srepkg_path / '__init__.py'
        inner_setup_cfg_active = srepkg_path / 'setup.cfg'
        inner_setup_py_active = srepkg_path / 'setup.py'

        assert builder_dest_paths.root == t_data.t_proj_srepkg_info.srepkg_root
        assert builder_dest_paths.srepkg == srepkg_path
        assert builder_dest_paths.srepkg_control_components == \
               srepkg_control_components
        assert builder_dest_paths.entry_module == srepkg_entry_module
        assert builder_dest_paths.srepkg_entry_points == srepkg_entry_points
        assert builder_dest_paths.srepkg_setup_cfg == srepkg_setup_cfg
        assert builder_dest_paths.srepkg_setup_py == srepkg_setup_py
        assert builder_dest_paths.srepkg_init == srepkg_init
        assert builder_dest_paths.inner_setup_cfg_active == \
               inner_setup_cfg_active
        assert builder_dest_paths.inner_setup_py_active == \
               inner_setup_py_active
