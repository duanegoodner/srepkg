import configparser
from pathlib import Path
from typing import NamedTuple, List
from srepkg.srepkg_builders import ep_console_script as epcs


class OrigPkgInfo(NamedTuple):
    pkg_name: str
    root_path: Path
    entry_pts: List[epcs.CSEntry]


class OrigPkgInspector:

    def __init__(self, orig_pkg: str):
        self._orig_pkg = orig_pkg

    @property
    def orig_pkg_path(self):
        return Path(self._orig_pkg)

    def validate_orig_pkg_path(self):
        if not self.orig_pkg_path.exists():
            print('Original package path not found.')
            exit(1)
        return self

    def validate_setup_cfg(self):
        if not (self.orig_pkg_path.parent.absolute() / 'setup.cfg').exists():
            print('Original package path not found.')
            exit(1)
        return self

    def get_orig_pkg_info(self):
        pkg_name = ''
        config = configparser.ConfigParser()

        root_path = self.orig_pkg_path.parent.absolute()
        try:
            config.read(root_path / 'setup.cfg')
        except (FileNotFoundError, KeyError, Exception):
            print(f'Unable to read setup.cfg file')
            exit(1)

        try:
            pkg_name = config['metadata']['name']
        except (KeyError, Exception):
            print('Unable to read package name')
            exit(1)

        cse_list = []
        try:
            ep_cs_list = config['options.entry_points']['console_scripts'] \
                .strip().splitlines()
            cse_list = [epcs.parse_cs_line(entry) for entry in ep_cs_list]
        except (TypeError, Exception):
            print('Unable to find any console script entry point for original'
                  'package')
            # TODO if inner pkg __main__ exists, just warn instead of exit
            exit(1)

        return OrigPkgInfo(pkg_name=pkg_name, root_path=root_path,
                           entry_pts=cse_list)

