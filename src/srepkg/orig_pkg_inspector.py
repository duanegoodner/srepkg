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


class PkgInspectorMsg(NamedTuple):
    msg: str


class PkgError(PkgInspectorMsg, Enum):
    PkgNameNotFound = PkgInspectorMsg(
        msg='Unable to find package name in setup.cfg')
    InvalidPkgName = PkgInspectorMsg(msg='Invalid package name')
    PkgPathNotFound = PkgInspectorMsg(msg='Original package path not found')
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


class SetupFilesReader:

    def __init__(self, orig_pkg_path: Path, cfg_keys: SetupKeys,
                 py_keys: SetupKeys):
        self._orig_pkg_path = orig_pkg_path
        self._data_keys = SetupDataKeys(cfg=cfg_keys, py=py_keys)
        self._setup_data = SetupData(cfg={}, py={})

    def _read_raw_setup_py(self):
        if not (self._orig_pkg_path / 'setup.py').exists():
            sys.exit(PkgError.SetupPyNotFound.msg)

        try:
            sys.path.insert(0, str(self._orig_pkg_path))
            with mock.patch.object(setuptools, 'setup') as mock_setup:
                import setup
                setup_params = mock_setup.call_args[1]
        finally:
            sys.path.remove(str(self._orig_pkg_path))
            sys.modules.pop('setup')

        self._setup_data.py.update(setup_params)

    def _read_raw_setup_cfg(self):
        config = configparser.ConfigParser()

        try:
            config.read(self._orig_pkg_path / 'setup.cfg')
        except (configparser.ParsingError,
                configparser.MissingSectionHeaderError):
            sys.exit(PkgError.SetupCfgReadError.msg)

        self._setup_data.cfg.update({sect: dict(config.items(sect)) for sect in
                                     config.sections()})

    def _filter_all_setup_data(self):
        for field in self._data_keys._fields:
            filtered_data = filter_setup_data(
                getattr(self._setup_data, field),
                getattr(self._data_keys, field))

            getattr(self._setup_data, field).clear()
            getattr(self._setup_data, field).update(filtered_data)

    def _cfg_cs_str_to_list(self):
        if type(self._setup_data.cfg['console_scripts']) == str:
            self._setup_data.cfg['console_scripts'] =\
                self._setup_data.cfg['console_scripts'].strip().splitlines()

    def _cfg_pkg_dir_str_to_list(self):
        dir_dict = {}
        cfg_dir_data = self._setup_data.cfg['package_dir']

        if cfg_dir_data and type(cfg_dir_data) == str:
            pkg_dir_lines = cfg_dir_data.strip().split('\n')
            pkg_dir_lines_parsed = [[item.strip() for item in line] for line in
                                    [line.split('=') for line in pkg_dir_lines]]

            for line in pkg_dir_lines_parsed:
                if len(line) == 2:
                    pkg_name = line[0]
                    pkg_dir = line[1]
                elif len(line) == 1:
                    pkg_name = ''
                    pkg_dir = line[0]
                else:
                    sys.exit(PkgError.InvalidPackageDirValue.msg)

                # guard against repeat entry (val overwrite) of key already in dict
                if pkg_name in dir_dict:
                    sys.exit(PkgError.InvalidPackageDirValue.msg)
                else:
                    dir_dict[pkg_name] = pkg_dir

            self._setup_data.cfg['package_dir'] = dir_dict

    def _cs_lists_to_cse_objs(self):
        for field in self._setup_data._fields:
            cs_data = getattr(self._setup_data, field).get('console_scripts')
            if cs_data and type(cs_data[0]) == str:
                cse_list = [su.ep_console_script.parse_cs_line(entry)
                            for entry in cs_data]
                getattr(self._setup_data, field)['console_scripts'] = cse_list

    def _merge_cfg_and_py(self):
        return {**self._setup_data.py, **self._setup_data.cfg}

    def get_setup_params(self):
        self._read_raw_setup_py()
        self._read_raw_setup_cfg()
        self._filter_all_setup_data()
        self._cfg_cs_str_to_list()
        self._cfg_pkg_dir_str_to_list()
        self._cs_lists_to_cse_objs()
        return self._merge_cfg_and_py()


class OrigPkgInspector:
    _cfg_keys = SetupKeys(
        single_level=[],
        two_level=[('metadata', 'name'), ('options', 'package_dir'),
                   ('options.entry_points', 'console_scripts')])

    _py_keys = SetupKeys(
        single_level=['name', 'package_dir', 'dummy'],
        two_level=[('entry_points', 'console_scripts')])

    def __init__(self, orig_pkg_path: str):
        self._orig_pkg_path = Path(orig_pkg_path)

    def validate_orig_pkg_path(self):
        if not self._orig_pkg_path.exists():
            sys.exit(PkgError.PkgPathNotFound.msg)
        return self

    def validate_setup_cfg(self):
        if not (self._orig_pkg_path.absolute() / 'setup.cfg').exists():
            sys.exit(PkgError.SetupCfgNotFound.msg)
        return self

    def validate_setup_py(self):
        if not (self._orig_pkg_path.absolute() / 'setup.py').exists():
            sys.exit(PkgError.SetupPyNotFound)
        return self

    def get_orig_pkg_info(self):
        self.validate_orig_pkg_path().validate_setup_cfg().validate_setup_py()

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
