import configparser
from pathlib import Path
from typing import NamedTuple
from enum import Enum
import sys
import srepkg.shared_utils as su


class PkgInspectorMsg(NamedTuple):
    msg: str


class PkgError(PkgInspectorMsg, Enum):
    PkgNameNotFound = PkgInspectorMsg(
        msg='Unable to find package name in setup.cfg')
    InvalidPkgName = PkgInspectorMsg(msg='Invalid package name')
    PkgPathNotFound = PkgInspectorMsg(msg='Original package path not found')
    SetupCfgNotFound = PkgInspectorMsg(
        msg='Original package\'s setup.cfg file not found')
    SetupCfgReadError = PkgInspectorMsg(msg='Unable to read or parse setup.cfg')
    NoCommandLineAccess = PkgInspectorMsg(
        msg='Srepkg requires original package to have at least one command line'
            ' access point. None found. No __main__.py found in top level '
            'package, and no console_script entry_points found')


class PkgWarning(PkgInspectorMsg, Enum):
    CSENotFound = PkgInspectorMsg(
        msg='Unable to find [options.entry_points]console_scripts\n'
            'in setup.cfg. If original package has a top-level __main__.py\n'
            'file, this is OK. Otherwise, srepkg will exit.')
    CSEBlank = PkgInspectorMsg(
        msg='[options.entry_points]console_scripts value in setup.cfg is\n'
            'empty. If original package has a top-level __main__.py. file,\n'
            'this is OK. Otherwise, srepkg will exit.')
    NoTopLevelMain = PkgInspectorMsg(
        msg='No top level __main__.py file found. If original package has\n'
            'console_script entry_point(s), this is OK. Otherwise, srepkg\n'
            'will exit.')


class PkgItemFound(PkgInspectorMsg, Enum):
    CSEFound = PkgInspectorMsg(msg='Console script entry point(s) found in '
                                   'setup.cfg')
    MainFileFound = PkgInspectorMsg(msg='Top level __main__.py found')


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


def get_package_dir(populated_config: configparser.ConfigParser) -> str:
    try:
        package_dir = populated_config['options']['package_dir']
    except KeyError:
        return ''
    return package_dir


def get_cse_list(populated_config: configparser.ConfigParser):
    try:
        ep_cs_list = \
            populated_config['options.entry_points']['console_scripts'] \
            .strip().splitlines()
    except KeyError:
        # OK if orig pkg has __main__.py. get_orig_pkg_info() checks for that
        ep_cs_list = []

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
        package_dir_path = self._orig_pkg_path / get_package_dir(config)

        # must run get_pkg_name() before get_cse_list() b/c former exits on an
        # Exception type that the latter allows
        pkg_name = get_pkg_name(config)
        entry_pts = get_cse_list(config)

        has_main = (package_dir_path / '__main__.py').exists()

        if not has_main and len(entry_pts) == 0:
            sys.exit(PkgError.NoCommandLineAccess.msg)

        return su.named_tuples.OrigPkgInfo(
            pkg_name=pkg_name,
            root_path=self._orig_pkg_path,
            package_dir_path=package_dir_path,
            entry_pts=entry_pts,
            has_main=has_main
        )
