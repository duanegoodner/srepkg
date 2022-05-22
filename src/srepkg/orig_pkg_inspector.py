from pathlib import Path
from typing import NamedTuple, List
from enum import Enum

import sys
import srepkg.shared_utils as su
import srepkg.setup_file_reader as sfr


class PkgError(su.nt.ErrorMsg, Enum):
    PkgPathNotFound = su.nt.ErrorMsg(msg='Original package path not found')
    NoSetupFilesFound = su.nt.ErrorMsg(
        msg='No setup.py file found, and no setup.cfg file found.\nsrepkg needs'
            ' at least one of these files.')
    PkgNameNotFound = su.nt.ErrorMsg(
        msg='Unable to find package name in any setup file')
    InvalidPkgName = su.nt.ErrorMsg(msg='Invalid package name')
    SetupCfgReadError = su.nt.ErrorMsg(msg='Unable to read or parse setup.cfg')
    NoCSE = su.nt.ErrorMsg(msg='No console script entry points found')


class PkgWarning(su.nt.ErrorMsg, Enum):
    SetupCfgReadError = su.nt.ErrorMsg(
        msg='Problem reading setup.cfg. srepkg is unable to obtain any data '
            'from this file')


class SetupKeys(NamedTuple):
    single_level: List[str]
    two_level: List[tuple[str, str]]


class SetupDataKeys(NamedTuple):
    cfg: SetupKeys
    py: SetupKeys


class SetupData(NamedTuple):
    cfg: dict
    py: dict


class OrigPkgInspector:
    _setup_filenames = ['setup.cfg', 'setup.py']

    def __init__(self, orig_pkg_path: str):
        self._orig_pkg_path = Path(orig_pkg_path)
        self._all_setup_data = {}
        self._merged_setup_data = {}

    def _validate_orig_pkg_path(self):
        if not self._orig_pkg_path.exists():
            sys.exit(PkgError.PkgPathNotFound.msg)
        return self

    def _validate_setup_files(self):
        setup_paths_found = [(self._orig_pkg_path / filename).exists() for
                             filename in self._setup_filenames]
        if not any(setup_paths_found):
            sys.exit(PkgError.NoSetupFilesFound.msg)
        return self

    def _get_all_setup_data(self):
        self._validate_orig_pkg_path()._validate_setup_files()

        for filename in self._setup_filenames:
            self._all_setup_data[filename] = sfr.SetupFileReader(
                self._orig_pkg_path / filename
            ).get_setup_info()

        return self

    def _merge_all_setup_data(self):
        self._merged_data = {**self._all_setup_data['setup.cfg'],
                             **self._all_setup_data['setup.py']}
        return self

    def _validate_merged_data(self):
        if ('name' not in self._merged_data) or \
                (not self._merged_data['name']):
            sys.exit(PkgError.PkgNameNotFound.msg)

        if ('console_scripts' not in self._merged_data) or\
                (not self._merged_data['console_scripts']):
            sys.exit(PkgError.NoCSE.msg)

        return self

    def get_orig_pkg_info(self):
        self._get_all_setup_data()._merge_all_setup_data() \
            ._validate_merged_data()

        return su.named_tuples.OrigPkgInfo(
            pkg_name=self._merged_data['name'],
            root_path=self._orig_pkg_path,
            entry_pts=self._merged_data['console_scripts'])
