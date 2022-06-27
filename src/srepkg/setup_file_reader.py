import abc
import configparser
import os

import setuptools
import sys
import warnings
from enum import Enum
from typing import NamedTuple, List
from pathlib import Path
from unittest import mock
import shared_data_structures as cd
from error_handling.error_messages import SetupFileReaderError
from error_handling.custom_exceptions import UnsupportedSetupFileType


class SetupKeys(NamedTuple):
    single_level: List[str]
    two_level: List[tuple[str, str]]


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
            keys[1]: orig.get(keys[0]).get(keys[1])
            for keys in setup_keys.two_level
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

    @abc.abstractmethod
    def _convert_cs_entries_to_objs(self):
        pass

    def _cs_lists_to_cse_objs(self):
        if ("console_scripts" in self._data) and self._data["console_scripts"]:
            self._convert_cs_entries_to_objs()
        return self

    def get_setup_info(self):
        self._read_raw_data()._filter_raw_data()._cs_lists_to_cse_objs()
        return self._data


class _SetupCfgFileReader(_SetupFileReader):
    _doi_keys = SetupKeys(
        single_level=[],
        two_level=[
            ("metadata", "name"),
            ("metadata", "url"),
            ("metadata", "author"),
            ("metadata", "author_email"),
            ("metadata", "long_description"),
            ("options.entry_points", "console_scripts"),
        ],
    )

    def __init__(self, setup_file: Path):
        super().__init__(setup_file)

    def _read_raw_data(self):
        config = configparser.ConfigParser()

        try:
            config.read(self._setup_file)
        except (
            configparser.ParsingError,
            configparser.MissingSectionHeaderError,
        ):
            warnings.warn(
                SetupFileReaderError.SetupCfgReadError.msg, UserWarning
            )

        self._data.clear()
        self._data.update(
            {sect: dict(config.items(sect)) for sect in config.sections()}
        )
        return self

    def _convert_cs_entries_to_objs(self):
        self._data["console_scripts"] = cd.console_script_entry.CSEntryPoints\
            .from_cfg_string(
            self._data["console_scripts"]).as_cse_obj_list

    def _convert_cs_str_to_list(self):
        if ("console_scripts" in self._data) and (
            type(self._data["console_scripts"]) == str
        ):
            self._data["console_scripts"] = cd.console_script_entry\
                .CSEntryPoints.from_cfg_string(self._data["console_scripts"])\
                .as_string_list

        return self

    def _match_to_py_format(self):
        self._convert_cs_str_to_list()

        return self


class _SetupPyFileReader(_SetupFileReader):
    _doi_keys = SetupKeys(
        single_level=[
            "name",
            "version",
            "author",
            "author_email",
            "url",
            "long_description",
        ],
        two_level=[("entry_points", "console_scripts")],
    )

    def __init__(self, setup_file: Path):
        super().__init__(setup_file)

    def _read_raw_data(self):
        cwd = Path.cwd()
        os.chdir(str(self._setup_file.parent))
        setup_params = {}

        if self._setup_file.exists():

            try:
                sys.path.insert(0, str(self._setup_file.parent.absolute()))
                with mock.patch.object(setuptools, "setup") as mock_setup:
                    import setup

                    if mock_setup.call_args:
                        setup_params = mock_setup.call_args[1]
            finally:
                sys.path.remove(str(self._setup_file.parent.absolute()))
                if "setup" in sys.modules:
                    sys.modules.pop("setup")

            self._data.clear()
            if setup_params:
                self._data.update(setup_params)

        os.chdir(cwd)

        return self

    def _convert_cs_entries_to_objs(self):
        self._data["console_scripts"] = cd.console_script_entry.CSEntryPoints\
            .from_string_list(self._data["console_scripts"]).as_cse_obj_list

    def _match_to_py_format(self):
        return self  # setup.py data already in py format


class SetupFileReader:
    _file_type_readers = {
        ".cfg": _SetupCfgFileReader,
        ".py": _SetupPyFileReader,
    }

    def __init__(self, setup_file: Path):
        self._setup_file = setup_file

    @property
    def _implemented_reader(self) -> _SetupFileReader:
        return self._file_type_readers[self._setup_file.suffix](
            self._setup_file
        )

    def _validate_file_type(self):
        if self._setup_file.suffix not in self._file_type_readers:
            raise UnsupportedSetupFileType(self._setup_file.name)

    def get_setup_info(self):
        try:
            self._validate_file_type()
        except UnsupportedSetupFileType:
            return

        return self._implemented_reader.get_setup_info()
