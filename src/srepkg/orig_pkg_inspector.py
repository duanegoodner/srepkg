import configparser
from pathlib import Path
from typing import NamedTuple
from enum import Enum
import sys
import srepkg.shared_utils as su


PkgErrorMsg = NamedTuple('PkgErrorMsg', [('msg', str)])


class PkgError(PkgErrorMsg, Enum):
    PkgNameNotFound = PkgErrorMsg(msg='Unable to find package name in setup.cfg')
    InvalidPkgName = PkgErrorMsg(msg='Invalid package name')
    CSENotFound = PkgErrorMsg(msg='Unable to find any console script entry '
                                  'point for original')
    PkgPathNotFound = PkgErrorMsg(msg='Original package path not found')
    SetupCfgNotFound = PkgErrorMsg(msg='Original package setup.cfg file not '
                                       'found')
    SetupCfgReadError = PkgErrorMsg(msg='Unable to read or parse setup.cfg')


def get_pkg_name(populated_config: configparser.ConfigParser) -> str:
    """


    :param populated_config: a ConfigParser that has previously read data from
    a setup.cfg file
    :return: value name in the metadata section of setup.cfg
    :raises
    """
    try:
        pkg_name = populated_config['metadata']['name']
    except KeyError:
        sys.exit(PkgError.PkgNameNotFound.msg)
    if len(pkg_name) == 0:
        sys.exit(PkgError.InvalidPkgName.msg)
    return pkg_name


def get_cse_list(populated_config: configparser.ConfigParser):
    try:
        ep_cs_list = \
            populated_config['options.entry_points']['console_scripts'] \
            .strip().splitlines()
    except KeyError:
        sys.exit(PkgError.CSENotFound.msg)
        # TODO if inner pkg __main__ exists, just warn instead of exit

    return [su.ep_console_script.parse_cs_line(entry) for entry in ep_cs_list]


class OrigPkgInspector:

    def __init__(self, orig_pkg_path: str):
        self._orig_pkg_path = Path(orig_pkg_path)

    def validate_orig_pkg_path(self):
        if not self._orig_pkg_path.exists():
            raise SystemExit(PkgError.PkgPathNotFound.msg)
        return self

    def validate_setup_cfg(self):
        if not (self._orig_pkg_path.absolute() / 'setup.cfg').exists():
            sys.exit(PkgError.SetupCfgNotFound.msg)
        return self

    def read_orig_cfg(self):
        config = configparser.ConfigParser()

        try:
            config.read(self._orig_pkg_path / 'setup.cfg')
        except (configparser.ParsingError,
                configparser.MissingSectionHeaderError):
            sys.exit(PkgError.SetupCfgReadError.msg)

        return config

    def get_orig_pkg_info(self):
        self.validate_orig_pkg_path().validate_setup_cfg()
        config = self.read_orig_cfg()

        return su.named_tuples.OrigPkgInfo(
            pkg_name=get_pkg_name(config),
            root_path=self._orig_pkg_path,
            entry_pts=get_cse_list(config))
