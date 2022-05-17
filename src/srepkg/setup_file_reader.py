import abc
import configparser
import setuptools
import sys
from enum import Enum
from typing import NamedTuple, List
from pathlib import Path
from unittest import mock

import srepkg.shared_utils as su


class SetupFileReaderMsg(NamedTuple):
    msg: str


class SetupFileReaderError(SetupFileReaderMsg, Enum):
    SetupCfgReadError = SetupFileReaderMsg(
        msg='Unable to read or parse setup.cfg')
    InvalidPackageDirValue = SetupFileReaderMsg(
        msg='Invalid package_dir value in [options] section of setup.cfg'
    )


class SetupKeys(NamedTuple):
    single_level: List[str]
    two_level: List[tuple[str, str]]


def filter_and_flatten(orig: dict, setup_keys: SetupKeys):
    single_key_params = {
        key: orig.get(key) for key in setup_keys.single_level if key in orig
    }
    two_key_nested_params = {
        keys[1]: orig.get(keys[0]).get(keys[1]) for keys in setup_keys.two_level
        if (keys[0] in orig) and keys[1] in orig[keys[0]]
    }

    return {**single_key_params, **two_key_nested_params}


class SetupFileReader(abc.ABC):
    def __init__(self, setup_file: Path, doi_keys: SetupKeys):
        self._setup_file = setup_file
        self._doi_keys = doi_keys
        self._data = {}

    @abc.abstractmethod
    def _read_raw_data(self):
        return self

    def _filter_raw_data(self):
        filtered_data = filter_and_flatten(self._data, self._doi_keys)
        self._data.clear()
        self._data.update(filtered_data)
        return self

    @abc.abstractmethod
    def _match_to_py_format(self):
        return self

    def _cs_lists_to_cse_objs(self):
        if self._data['console_scripts'] and \
                (type(self._data['console_scripts']) == str):
            cse_list = [su.ep_console_script.parse_cs_line(entry) for entry in
                        self._data['console_scripts']]
            self._data['console_scripts'] = cse_list

    def get_data(self):
        self._read_raw_data()._filter_raw_data()._match_to_py_format()

        return self._data


class SetupCfgFileReader(SetupFileReader):

    def __init__(self, setup_file: Path, doi_keys: SetupKeys):
        super().__init__(setup_file, doi_keys)

    def _read_raw_data(self):
        config = configparser.ConfigParser()

        try:
            config.read(self._setup_file)
        except (configparser.ParsingError,
                configparser.MissingSectionHeaderError):
            # TODO consider changing this to just a warning
            sys.exit(SetupFileReaderError.SetupCfgReadError.msg)

        self._data.clear()
        self._data.update({sect: dict(config.items(sect)) for sect in
                           config.sections()})
        return self

    def _convert_cs_str_to_list(self):
        if ('console_scripts' in self._data)\
                and (type(self._data['console_scripts']) == str):
            self._data['console_scripts'] =\
                self._data['console_scripts'].strip().splitlines()

        return self

    def _convert_pkg_dir_str_to_dict(self):
        dir_dict = {}
        if ('package_dir' in self._data) and \
                (type(self._data['package_dir']) == str):
            pkg_dir_lines = self._data['package_dir'].strip() \
                .split('\n')
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
                    sys.exit(SetupFileReaderError.InvalidPackageDirValue.msg)

                # guard against repeat entry (val overwrite) of key already in dict
                if pkg_name in dir_dict:
                    sys.exit(SetupFileReaderError.InvalidPackageDirValue.msg)
                else:
                    dir_dict[pkg_name] = pkg_dir

            self._data['package_dir'] = dir_dict

        return self

    def _match_to_py_format(self):
        self._convert_cs_str_to_list()._convert_pkg_dir_str_to_dict()

        return self


class SetupPyFileReader(SetupFileReader):
    def __init__(self, setup_file: Path, doi_keys: SetupKeys):
        super().__init__(setup_file, doi_keys)

    def _read_raw_data(self):
        try:
            sys.path.insert(0, str(self._setup_file.parent.absolute()))
            with mock.patch.object(setuptools, 'setup') as mock_setup:
                import setup
                setup_params = mock_setup.call_args[1]
        finally:
            sys.path.remove(str(self._setup_file.parent.absolute()))
            sys.modules.pop('setup')

        self._data.clear()
        self._data.update(setup_params)

        return self

    def _match_to_py_format(self):
        return self  # setup.py data already in py format


class SetupInfo:
    def __init__(self, pkg_name: str = None, package_dir: str = None,
                 console_scripts=None):
        if console_scripts is None:
            console_scripts = []
        self._pkg_name = pkg_name
        self._package_dir = package_dir
        self._console_scripts = console_scripts

    @classmethod
    def from_setup_file_reader_data(cls, sfr_data: dict):
        pkg_name = sfr_data['name'] if 'name' in sfr_data else None
        package_dir = sfr_data['package_dir'] if 'package_dir' \
                                                 in sfr_data else None
        console_scripts = sfr_data['console_scripts'] if 'console_scripts' \
                                                         in sfr_data else None
        return cls(pkg_name=pkg_name, package_dir=package_dir,
                   console_scripts=console_scripts)
