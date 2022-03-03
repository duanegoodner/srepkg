import unittest
import shutil
import configparser
from operator import attrgetter
from pathlib import Path
from srepkg.test.test_path_calculator import p_calc
from srepkg.srepkg_builder import SrepkgBuilder
import srepkg.ep_console_script as epcs

my_orig_pkg = Path.home() / 'dproj' / 'my_project' / 'my_project'
inner_pkg = Path.home() / 'srepkg_pkgs' / \
            (my_orig_pkg.name + '_as_' + my_orig_pkg.name + 'srnew')
srepkg_path = Path(__file__).parent.parent.absolute()


class TestSrepkgBuilder(unittest.TestCase):

    def setUp(self) -> None:
        if inner_pkg.exists():
            shutil.rmtree(inner_pkg)
        self.orig_pkg_info, self.src_paths, self.h_paths = p_calc(my_orig_pkg)
        self.srepkg_builder = SrepkgBuilder(self.orig_pkg_info, self.src_paths,
                                            self.h_paths)

    def test_srepkg_builder_paths(self):
        assert self.srepkg_builder.src_paths == self.src_paths
        assert self.srepkg_builder.repkg_paths == self.h_paths

    def test_inner_pkg_copy(self):
        self.srepkg_builder.copy_inner_package()
        assert self.srepkg_builder.repkg_paths.root.exists()
        assert self.srepkg_builder.repkg_paths.srepkg.exists()
        assert self.srepkg_builder.repkg_paths.orig_pkg_setup_py.exists()
        assert self.srepkg_builder.repkg_paths.orig_pkg_setup_cfg.exists()

    def test_modify_inner_pkg(self):
        self.srepkg_builder.copy_inner_package()
        self.srepkg_builder.modify_inner_pkg()
        assert not self.srepkg_builder.repkg_paths.orig_pkg_setup_py.exists()
        assert (self.srepkg_builder.repkg_paths.orig_pkg_setup_cfg.parent /
                'setup_off.py').exists()
        assert not self.srepkg_builder.repkg_paths.orig_pkg_setup_cfg.exists()
        assert (self.srepkg_builder.repkg_paths.orig_pkg_setup_cfg.parent /
                'setup_off.cfg').exists()

    def test_orig_config_read(self):
        orig_config = configparser.ConfigParser()
        orig_config.read(self.srepkg_builder.orig_pkg_info.root_path /
                         'setup.cfg')
        orig_config_sections = orig_config.sections()
        assert len(orig_config_sections) == 4
        assert 'metadata' in orig_config_sections
        assert 'options' in orig_config_sections
        assert 'options.entry_points' in orig_config_sections
        assert 'options.package_data' in orig_config_sections

    def test_setup_template_config_read(self):
        sr_config = configparser.ConfigParser()
        sr_config.read(self.srepkg_builder.src_paths.srepkg_setup_cfg)
        sr_config_sections = sr_config.sections()
        assert len(sr_config_sections) == 4
        assert 'metadata' in sr_config_sections
        assert 'options' in sr_config_sections
        assert 'options.entry_points' in sr_config_sections
        assert 'options.package_data' in sr_config_sections

    def test_build_sr_cfg(self):
        self.srepkg_builder.copy_inner_package()
        self.srepkg_builder.modify_inner_pkg()
        self.srepkg_builder.build_sr_cfg()

        assert self.srepkg_builder.repkg_paths.srepkg_setup_cfg.exists()

        outer_config_cse_list = epcs.cfg_cs_list_to_cse_list(
            self.srepkg_builder.repkg_paths.srepkg_setup_cfg)

        orig_config_cse_list = epcs.cfg_cs_list_to_cse_list(
            self.srepkg_builder.orig_pkg_info.root_path / 'setup.cfg')

        assert len(outer_config_cse_list) == len(orig_config_cse_list)

        outer_config_cse_list.sort(key=attrgetter('command'))
        orig_config_cse_list.sort(key=attrgetter('command'))

        assert [entry.command for entry in outer_config_cse_list] == \
               [entry.command + '_sr' for entry in orig_config_cse_list]

        assert [entry.module_path for entry in outer_config_cse_list] == \
               [self.h_paths.srepkg.name +
                '.' + self.h_paths.srepkg_entry_points.name + '.' + orig_entry.funct
                for orig_entry in orig_config_cse_list]

        assert [entry.funct for entry in outer_config_cse_list] == \
               ['entry_funct' for entry in orig_config_cse_list]

    def test_add_srepkg_layer(self):
        self.srepkg_builder.copy_inner_package()
        self.srepkg_builder.modify_inner_pkg()
        self.srepkg_builder.build_sr_cfg()
        self.srepkg_builder.add_srepkg_layer()
