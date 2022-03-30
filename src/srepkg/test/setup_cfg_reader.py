
import shutil
import configparser
from pathlib import Path
from src.srepkg.test.test_path_calculator_old import m_paths
from src.srepkg import SrepkgBuilder

my_orig_pkg = Path.home() / 'dproj' / 'my_project' / 'my_project'
inner_pkg = Path.home() / 'srepkg_pkgs' /\
                  (my_orig_pkg.name + '_as_' + my_orig_pkg.name + 'srepkg')
srepkg_path = Path(__file__).parent.parent.absolute()

if inner_pkg.exists():
    shutil.rmtree(inner_pkg)
    
src_paths, h_paths = m_paths(my_orig_pkg)
srepkg_builder = SrepkgBuilder(src_paths, h_paths)

print(srepkg_builder.src_paths.orig_setup_cfg_active)

config = configparser.ConfigParser()
config.read(srepkg_builder.src_paths.orig_setup_cfg)
print(config.sections())

print(srepkg_builder.src_paths.setup_cfg_outer)
config_2 = configparser.ConfigParser()
config_2.read(srepkg_builder.src_paths.setup_cfg_outer)
print(config_2.sections())

for key in config['options.entry_points']:
    print(config['options.entry_points'][key])
