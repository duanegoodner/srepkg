import configparser
import os
import shutil

import setuptools
from pathlib import Path
from typing import NamedTuple, List
from enum import Enum
from unittest import mock
import sys
import srepkg.shared_utils as su
import src.srepkg.setup_file_reader as sfr


class PkgInspectorMsg(NamedTuple):
    msg: str


class PkgError(PkgInspectorMsg, Enum):
    PkgPathNotFound = PkgInspectorMsg(msg='Original package path not found')
    NoSetupFilesFound = PkgInspectorMsg(
        msg='No setup.py file found, and no setup.cfg file found.\nsrepkg needs'
            ' at least one of these files.')
    PkgNameNotFound = PkgInspectorMsg(
        msg='Unable to find package name in setup.cfg')
    InvalidPkgName = PkgInspectorMsg(msg='Invalid package name')

    SetupPyNotFound = PkgInspectorMsg(
        msg='Original package\'s setup.py file not found')
    SetupCfgNotFound = PkgInspectorMsg(
        msg='Original package\'s setup.cfg file not found')
    SetupCfgReadError = PkgInspectorMsg(msg='Unable to read or parse setup.cfg')
    NoCommandLineAccess = PkgInspectorMsg(
        msg='Srepkg requires original package to have at least one command line'
            ' access point. None found. No __main__.py found in top level '
            'package, and no console_script entry_points found')
    InvalidPackageDirValue = PkgInspectorMsg(
        msg='invalid package_dir value in [options] section of setup.cfg')


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


class PkgDirInfoExtractor:

    def __init__(self, package_dir_dict: dict, pkg_name: str):
        self._dir_dict = package_dir_dict
        self._pkg_name = pkg_name

    def _validate_dir_dict(self):
        if '' in self._dir_dict and len(self._dir_dict) > 1:
            sys.exit(PkgError.InvalidPackageDirValue.msg)

    def get_top_level_pkg_dir(self):

        # dir_dict = self.parse_pkg_dir_entry()
        self._validate_dir_dict()

        if '' in self._dir_dict:
            return self._dir_dict['']

        if self._pkg_name in self._dir_dict:
            return self._dir_dict[self._pkg_name]

        return ''


class SetupKeys(NamedTuple):
    single_level: List[str]
    two_level: List[tuple[str, str]]


class SetupDataKeys(NamedTuple):
    cfg: SetupKeys
    py: SetupKeys


class SetupData(NamedTuple):
    cfg: dict
    py: dict


def filter_setup_data(orig: dict, setup_keys: SetupKeys):
    single_key_params = {
        key: orig.get(key) for key in setup_keys.single_level if key in orig
    }
    two_key_nested_params = {
        keys[1]: orig.get(keys[0]).get(keys[1]) for keys in setup_keys.two_level
        if (keys[0] in orig) and keys[1] in orig[keys[0]]
    }

    return {**single_key_params, **two_key_nested_params}


class OrigPkgInspector:
    _cfg_keys = SetupKeys(
        single_level=[],
        two_level=[('metadata', 'name'), ('options', 'package_dir'),
                   ('options.entry_points', 'console_scripts')])

    _py_keys = SetupKeys(
        single_level=['name', 'package_dir'],
        two_level=[('entry_points', 'console_scripts')])

    def __init__(self, orig_pkg_path: str):
        self._orig_pkg_path = Path(orig_pkg_path)
        self._all_setup_file_info = []

    def _validate_orig_pkg_path(self):
        if not self._orig_pkg_path.exists():
            sys.exit(PkgError.PkgPathNotFound.msg)
        return self

    def _validate_setup_files(self):
        if not (self._orig_pkg_path.absolute() / 'setup.cfg').exists() and not\
                (self._orig_pkg_path.absolute() / 'setup.py').exists():
            sys.exit(PkgError.NoSetupFilesFound.msg)
        return self

    @staticmethod
    def merge_setup_info(all_setup_info: List[sfr.SetupFileInfo]):


        def get_orig_pkg_info(self):
            self._validate_orig_pkg_path()_.validate_setup_files()

            cfg_setup_info = sfr.SetupCfgFileReader(
                setup_file=self._orig_pkg_path / 'setup.cfg',
                file_type=sfr.SetupFileType.CFG,
                doi_keys=self._cfg_keys).get_setup_info()

            py_setup_info = sfr.SetupPyFileReader(
                setup_file=self._orig_pkg_path / 'setup.py',
                file_type=sfr.SetupFileType.PY,
                doi_keys=self._py_keys).get_setup_info()





        setup_files_reader = SetupFilesReader(
            orig_pkg_path=self._orig_pkg_path,
            cfg_keys=self._cfg_keys,
            py_keys=self._py_keys)
        setup_params = setup_files_reader.get_setup_params()

        # TODO add method for validating setup_params

        pkg_dir_extractor = PkgDirInfoExtractor(
            setup_params['package_dir'], setup_params['name'])
        package_dir = pkg_dir_extractor.get_top_level_pkg_dir()

        package_dir_path = self._orig_pkg_path / package_dir

        # leftover comment from prev implementation. info may still be useful:
        # must run get_pkg_name() before get_cse_list() b/c former exits on an
        # Exception type that the latter allows

        has_main = (package_dir_path / setup_params['name']
                    / '__main__.py').exists()

        if not has_main and len(setup_params['console_scripts']) == 0:
            sys.exit(PkgError.NoCommandLineAccess.msg)

        return su.named_tuples.OrigPkgInfo(
            pkg_name=setup_params['name'],
            root_path=self._orig_pkg_path,
            package_dir_path=package_dir_path,
            entry_pts=setup_params['console_scripts'],
            has_main=has_main
        )
