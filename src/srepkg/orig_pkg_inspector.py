import sys

from pathlib import Path
from typing import NamedTuple, List

import shared_data_structures as cd
import srepkg.setup_file_reader as sfr
from error_handling.error_messages import OrigPkgError


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
    _setup_filenames = ["setup.cfg", "setup.py"]

    def __init__(self, orig_pkg_path: str):
        self._orig_pkg_path = Path(orig_pkg_path)
        self._all_setup_data = {}
        self._merged_setup_data = {}

    def _validate_orig_pkg_path(self):
        if not self._orig_pkg_path.exists():
            sys.exit(OrigPkgError.PkgPathNotFound.msg)
        return self

    def _validate_setup_files(self):
        setup_paths_found = [
            (self._orig_pkg_path / filename).exists()
            for filename in self._setup_filenames
        ]
        if not any(setup_paths_found):
            sys.exit(OrigPkgError.NoSetupFilesFound.msg)
        return self

    def _get_all_setup_data(self):
        self._validate_orig_pkg_path()._validate_setup_files()

        for filename in self._setup_filenames:
            self._all_setup_data[filename] = sfr.SetupFileReader(
                self._orig_pkg_path / filename
            ).get_setup_info()

        return self

    def _merge_all_setup_data(self):
        self._merged_data = {
            **self._all_setup_data["setup.cfg"],
            **self._all_setup_data["setup.py"],
        }
        return self

    def _validate_merged_data(self):
        if ("name" not in self._merged_data) or (not self._merged_data["name"]):
            sys.exit(OrigPkgError.PkgNameNotFound.msg)

        if ("console_scripts" not in self._merged_data) or (
            not self._merged_data["console_scripts"]
        ):
            sys.exit(OrigPkgError.NoCSE.msg)

        if ("version" not in self._merged_data) or (
            not self._merged_data["version"]
        ):
            self._merged_data["version"] = "0.0.0"

        return self

    def get_orig_pkg_info(self):
        self._get_all_setup_data()._merge_all_setup_data()\
            ._validate_merged_data()

        return cd.nt.OrigPkgInfo(
            pkg_name=self._merged_data["name"],
            version=self._merged_data["version"],
            root_path=self._orig_pkg_path,
            entry_pts=self._merged_data["console_scripts"],
        )
