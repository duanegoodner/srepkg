import unittest
import shutil
from pathlib import Path
from srepkg.test.persistent_locals import PersistentLocals
import srepkg.command_input as ci
import srepkg.path_calculator as pc


my_orig_pkg = Path.home() / 'dproj' / 'my_project' / 'my_project'
inner_pkg = Path.home() / 'srepkg_pkgs' /\
                  (my_orig_pkg.name + '_as_' + my_orig_pkg.name + 'srnew')
srepkg_path = Path(__file__).parent.parent.absolute()


@PersistentLocals
def m_paths(orig_pkg: Path):
    args = ci.get_args([str(orig_pkg)])
    my_orig_pkg_path, dest_path = pc.calc_root_paths_from(args)
    src_paths, h_paths = pc.create_builder_paths(my_orig_pkg_path, dest_path)

    return src_paths, h_paths


class TestPathCalc(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if inner_pkg.exists():
            shutil.rmtree(inner_pkg)

        m_paths(my_orig_pkg)

    def test_locals_accessible(self):
        print(m_paths.locals)

    def test_args(self):
        assert m_paths.locals['args'].orig_pkg_path == str(my_orig_pkg)
        assert m_paths.locals['args'].srepkg_name is None

    def test_root_paths(self):
        assert Path(m_paths.locals['my_orig_pkg_path']) == my_orig_pkg
        assert Path(m_paths.locals['dest_path']) == inner_pkg /\
               'my_projectsrnew'

    def test_builder_src_paths(self):
        src_paths = m_paths.locals['src_paths']

        assert src_paths.orig_setup_cfg == my_orig_pkg.parent / 'setup.cfg'
        assert src_paths.name_template == srepkg_path /\
               'install_components' / 'pkg_name.py.template'
        assert src_paths.srepkg_components == srepkg_path /\
               'install_components' / 'srepkg_components'
        assert src_paths.setup_py_outer == srepkg_path /\
               'install_components' / 'setup.py'
        assert src_paths.setup_cfg_outer == srepkg_path /\
               'install_components' / 'setup_template.cfg'
        assert src_paths.init == srepkg_path / 'install_components' /\
               'srepkg_init.py'

    def test_builder_h_paths(self):
        h_paths = m_paths.locals['h_paths']
        assert h_paths.init == inner_pkg /\
               (my_orig_pkg.name + 'srnew') / '__init__.py'
        assert h_paths.srepkg_components == inner_pkg /\
               (my_orig_pkg.name + 'srnew') / 'srepkg_components'
        assert h_paths.setup_cfg_outer == inner_pkg / 'setup.cfg'
        assert h_paths.setup_py_outer == inner_pkg / 'setup.py'
        assert h_paths.root == inner_pkg / (my_orig_pkg.name + 'srnew')
        assert h_paths.header == inner_pkg / (my_orig_pkg.name + 'srnew') /\
               'srepkg_components' / 'srepkg_header.py'
        assert h_paths.setup_py_inner == inner_pkg /\
               (my_orig_pkg.name + 'srnew') / 'setup.py'


if __name__ == '__main__':
    unittest.main()



