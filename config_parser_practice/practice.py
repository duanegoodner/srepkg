import configparser
from pathlib import Path


def build_sr_setup_cfg(orig_setup_cfg: Path, sr_pkg_name: str):
    orig_config = configparser.ConfigParser()
    orig_config.read(orig_setup_cfg)

    sr_config = configparser.ConfigParser()

    sr_config['metadata']['name'] = sr_pkg_name
    sr_config['metadata']['description'] = 'Repackaged by srepkg'

    sr_config['options']['packages'] = 'find:'
    sr_config['options']['include_package_data'] = 'True'

    sr_config['options.package_data']['*'] = '*.*'

    # for key in orig_config['options.entry_points']:
    #     sr_config['options.entry_points'][key + '_sr'] =










config = configparser.ConfigParser()
config.read('setup.cfg')



