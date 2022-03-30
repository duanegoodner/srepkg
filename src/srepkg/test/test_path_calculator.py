import shutil
import unittest
from pathlib import Path
import srepkg.test.t_proj_srepkg_info as tpsi
import srepkg.test.calc_test_paths as ctp


repackaging_components = Path(__file__).parent.parent.absolute() / \
                         'repackaging_components'


class TestPathCalculator(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        if tpsi.srepkg_root.exists():
            shutil.rmtree(tpsi.srepkg_root)

        ctp.calc_test_paths()

    def test_confirm_calc_paths_locals_accessible(self):
        print(ctp.calc_test_paths.locals)

    def test_builder_src_paths(self):
        builder_src_paths = ctp.calc_test_paths.locals['builder_src_paths']
        assert builder_src_paths.srepkg_init == repackaging_components / \
               'srepkg_init.py'
        assert builder_src_paths.entry_module == repackaging_components / \
               'srepkg_control_components' / 'entry_points.py'
        assert builder_src_paths.entry_point_template == \
               repackaging_components / 'entry_point_template.py'
        assert builder_src_paths.srepkg_control_components == \
               repackaging_components / 'srepkg_control_components'
        assert builder_src_paths.srepkg_setup_py == repackaging_components / \
               'setup.py'
        assert builder_src_paths.srepkg_setup_cfg == repackaging_components / \
               'setup_template.cfg'

    def test_builder_dest_paths(self):
        builder_dest_paths = ctp.calc_test_paths.locals['builder_dest_paths']

        srepkg_path = tpsi.srepkg_root / ('t_proj' + 'srepkg')
        srepkg_control_components = srepkg_path / 'srepkg_control_components'
        srepkg_entry_module = srepkg_control_components / 'entry_points.py'
        srepkg_entry_points = srepkg_path / 'srepkg_entry_points'
        srepkg_setup_cfg = tpsi.srepkg_root / 'setup.cfg'
        srepkg_setup_py = tpsi.srepkg_root / 'setup.py'
        srepkg_init = srepkg_path / '__init__.py'
        inner_setup_cfg_active = srepkg_path / 'setup.cfg'
        inner_setup_py_active = srepkg_path / 'setup.py'

        assert builder_dest_paths.root == tpsi.srepkg_root
        assert builder_dest_paths.srepkg == srepkg_path
        assert builder_dest_paths.srepkg_control_components ==\
               srepkg_control_components
        assert builder_dest_paths.entry_module == srepkg_entry_module
        assert builder_dest_paths.srepkg_entry_points == srepkg_entry_points
        assert builder_dest_paths.srepkg_setup_cfg == srepkg_setup_cfg
        assert builder_dest_paths.srepkg_setup_py == srepkg_setup_py
        assert builder_dest_paths.srepkg_init == srepkg_init
        assert builder_dest_paths.inner_setup_cfg_active ==\
               inner_setup_cfg_active
        assert builder_dest_paths.inner_setup_py_active ==\
               inner_setup_py_active
