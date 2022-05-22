import abc
import configparser
import setuptools
import sys
import warnings
from enum import Enum, auto
from typing import NamedTuple, List
from pathlib import Path
from unittest import mock
import srepkg.shared_utils as su


class SetupFileReaderError(su.nt.ErrorMsg, Enum):
    SetupCfgReadError = su.nt.ErrorMsg(
        msg='Unable to read or parse setup.cfg')
    InvalidPackageDirValue = su.nt.ErrorMsg(
        msg='Invalid package_dir value in [options] section of setup.cfg')
    UnsupportedSetupFileType = su.nt.ErrorMsg(
        msg='Unsupported setup file type'
    )


class SetupInfoError(su.nt.ErrorMsg, Enum):
    InvalidPkgDirValue = su.nt.ErrorMsg(
        msg='Invalid value for package_dir'
    )


class UnsupportedSetupFileType(Exception):
    def __init__(self, file_name: str, message='File type is not supported'):
        self.file_name = file_name
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.file_name} -> {self.message}'


class SetupKeys(NamedTuple):
    single_level: List[str]
    two_level: List[tuple[str, str]]


class SetupFileType(Enum):
    CFG = auto()
    PY = auto()


class _SetupFileReader(abc.ABC):
    def __init__(self, setup_file: Path):
        self._setup_file = setup_file
        self._data = {}

    @property
    @abc.abstractmethod
    def _doi_keys(self):
        return SetupKeys(single_level=[], two_level=[])

    @staticmethod
    def _filter_and_flatten(orig: dict, setup_keys: SetupKeys):
        single_key_params = {
            key: orig.get(key) for key in setup_keys.single_level if key in orig
        }
        two_key_nested_params = {
            keys[1]: orig.get(keys[0]).get(keys[1]) for keys in
            setup_keys.two_level
            if (keys[0] in orig) and keys[1] in orig[keys[0]]
        }

        return {**single_key_params, **two_key_nested_params}

    @abc.abstractmethod
    def _read_raw_data(self):
        return self

    def _filter_raw_data(self):
        filtered_data = self._filter_and_flatten(self._data, self._doi_keys)
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

    def get_setup_info(self):
        self._read_raw_data()._filter_raw_data()._match_to_py_format()
        return self._data


class _SetupCfgFileReader(_SetupFileReader):
    _doi_keys = SetupKeys(
        single_level=[],
        two_level=[('metadata', 'name'), ('options', 'package_dir'),
                   ('options.entry_points', 'console_scripts')])

    def __init__(self, setup_file: Path):
        super().__init__(setup_file)

    def _read_raw_data(self):
        config = configparser.ConfigParser()

        try:
            config.read(self._setup_file)
        except (configparser.ParsingError,
                configparser.MissingSectionHeaderError):
            # TODO consider changing this to just a warning
            # sys.exit(SetupFileReaderError.SetupCfgReadError.msg)
            warnings.warn(
                SetupFileReaderError.SetupCfgReadError.msg,
                UserWarning)

        self._data.clear()
        self._data.update({sect: dict(config.items(sect)) for sect in
                           config.sections()})
        return self

    def _convert_cs_str_to_list(self):
        if ('console_scripts' in self._data) \
                and (type(self._data['console_scripts']) == str):
            self._data['console_scripts'] = \
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


class _SetupPyFileReader(_SetupFileReader):

    _doi_keys = SetupKeys(
                    single_level=['name', 'package_dir', 'dummy'],
                    two_level=[('entry_points', 'console_scripts')])

    def __init__(self, setup_file: Path):
        super().__init__(setup_file)

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


class SetupFileReader:
    _file_type_readers = {
        '.cfg': _SetupCfgFileReader,
        '.py': _SetupPyFileReader
    }

    def __init__(self, setup_file: Path):
        self._setup_file = setup_file

    @property
    def _implemented_reader(self) -> _SetupFileReader:
        return self._file_type_readers[self._setup_file.suffix](
            self._setup_file)

    def _validate_file_type(self):
        if self._setup_file.suffix not in self._file_type_readers:
            raise UnsupportedSetupFileType(self._setup_file.name)

    def get_setup_info(self):
        try:
            self._validate_file_type()
        except UnsupportedSetupFileType:
            return

        return self._implemented_reader.get_setup_info()


class SetupFileInfo:
    _file_priority = [SetupFileType.PY, SetupFileType.CFG]

    def __init__(self, name: str = None, package_dir=None,
                 console_scripts=None):
        if console_scripts is None:
            console_scripts = []
        if package_dir is None:
            package_dir = {}
        self._name = name
        self._package_dir = package_dir
        self._console_scripts = console_scripts

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    @property
    def name(self):
        return self._name

    @property
    def package_dir(self):
        return self._package_dir

    @property
    def console_scripts(self):
        return self._console_scripts

    def _validate_package_dir(self):
        if '' in self._package_dir and len(self._package_dir) > 1:
            sys.exit(SetupInfoError.InvalidPkgDirValue.msg)
