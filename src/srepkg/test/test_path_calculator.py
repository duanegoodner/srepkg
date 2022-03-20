import unittest
import shutil
from pathlib import Path
from operator import attrgetter
from srepkg.test.persistent_locals import PersistentLocals
import srepkg.input.orig_pkg_inspector as ipi
import srepkg.input.command_input as ci
import srepkg.path_builders.path_calculator as pc
from srepkg.srepkg_builders import ep_console_script as epcs

proj_name_in_setup_cfg = 'my_project'
my_orig_pkg_setup_dir = Path.home() / 'dproj' / 'my_project'
srepkg_root = Path.home() / 'srepkg_pkgs' / (proj_name_in_setup_cfg + '_as_' +
                                             proj_name_in_setup_cfg + 'srepkg')

my_orig_pkg_cs = '\nmy_project = my_project.__main__:main\n' \
                 'my_test = my_project.test:first_test'
my_orig_pkg_cse = [epcs.parse_cs_line(entry) for entry in
                   my_orig_pkg_cs.strip().split('\n')]

srepkg_app_path = Path(__file__).parent.parent.absolute()


@PersistentLocals
def p_calc(orig_pkg_setup_dir: Path):
    args = ci.get_args([str(orig_pkg_setup_dir)])

    inner_pkg_inspector = ipi.OrigPkgInspector(args.orig_pkg_setup_dir) \
        .validate_orig_pkg_path().validate_setup_cfg()
    orig_pkg_info = inner_pkg_inspector.get_orig_pkg_info()

    builder_src_paths = pc.calc_builder_src_paths()

    dest_path_calculator = pc.DestPathCalculator(orig_pkg_info,
                                                 args.srepkg_name)
    dest_paths = dest_path_calculator.build_dest_paths()

    return orig_pkg_info, builder_src_paths, dest_paths


class TestPathCalculator(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        if srepkg_root.exists():
            shutil.rmtree(srepkg_root)

        p_calc(str(my_orig_pkg_setup_dir))

    def test_standard_path_calc_locals_accessible(self):
        print(p_calc.locals)

    def test_builder_src_paths(self):
        src_paths = p_calc.locals['builder_src_paths']
        repackaging_components = srepkg_app_path / 'repackaging_components'
        assert src_paths.srepkg_init == repackaging_components / 'srepkg_init.py'
        assert src_paths.entry_module == repackaging_components /\
               'srepkg_control_components' / 'entry_points.py'
        assert src_paths.entry_point_template == repackaging_components / \
               'entry_point_template.py'
        assert src_paths.srepkg_control_components == repackaging_components / \
               'srepkg_control_components'
        assert src_paths.srepkg_setup_py == repackaging_components / 'setup.py'
        assert src_paths.srepkg_setup_cfg == repackaging_components / \
               'setup_template.cfg'

    def test_orig_pkg_info(self):
        orig_pkg_info = p_calc.locals['orig_pkg_info']

        assert orig_pkg_info.pkg_name == proj_name_in_setup_cfg
        assert orig_pkg_info.root_path == my_orig_pkg_setup_dir.absolute()
        assert orig_pkg_info.entry_pts.sort(key=attrgetter('command')) ==\
               my_orig_pkg_cse.sort(key=attrgetter('command'))

    def test_dest_paths(self):
        dest_paths = p_calc.locals['dest_paths']

        srepkg_path = srepkg_root / ('my_project' + 'srepkg')
        srepkg_control_components = srepkg_path / 'srepkg_control_components'
        srepkg_entry_module = srepkg_control_components / 'entry_points.py'
        srepkg_entry_points = srepkg_path / 'srepkg_entry_points'
        srepkg_setup_cfg = srepkg_root / 'setup.cfg'
        srepkg_setup_py = srepkg_root / 'setup.py'
        srepkg_init = srepkg_path / '__init__.py'
        my_inner_setup_cfg_active = srepkg_path / 'setup.cfg'
        my_inner_setup_py_active = srepkg_path / 'setup.py'

        assert dest_paths.root == srepkg_root
        assert dest_paths.srepkg == srepkg_path
        assert dest_paths.srepkg_control_components == srepkg_control_components
        assert dest_paths.entry_module == srepkg_entry_module
        assert dest_paths.srepkg_entry_points == srepkg_entry_points
        assert dest_paths.srepkg_setup_cfg == srepkg_setup_cfg
        assert dest_paths.srepkg_setup_py == srepkg_setup_py
        assert dest_paths.srepkg_init == srepkg_init
        assert dest_paths.inner_setup_cfg_active == my_inner_setup_cfg_active
        assert dest_paths.inner_setup_py_active == my_inner_setup_py_active


if __name__ == '__main__':
    unittest.main()
