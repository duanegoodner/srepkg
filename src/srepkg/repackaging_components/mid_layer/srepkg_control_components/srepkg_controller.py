import subprocess
from pathlib import Path
from .srepkg_control_paths import VenvPaths


class SrepkgController:
    def __init__(
        self, srepkg_root: Path, inner_pkg_name: str, venv_paths: VenvPaths
    ):
        self._srepkg_root = srepkg_root
        self._inner_pkg_name = inner_pkg_name
        self._venv = venv_paths

    @classmethod
    def default(cls, srepkg_root: Path, inner_pkg_name: str):
        venv_root = srepkg_root / "srepkg_venv"
        return cls(
            srepkg_root=srepkg_root,
            inner_pkg_name=inner_pkg_name,
            venv_paths=VenvPaths.default(venv_root),
        )

    def run_inner_pkg_entry_point(self, entry_command: str, *pkg_args):
        subprocess.call([self._venv.vbin / entry_command, *pkg_args])
        return self

    def run_inner_pkg_main(self, *pkg_args):
        subprocess.call(
            [
                self._venv.py_interp,
                "-m",
                self._inner_pkg_name,
                "--called_by_safe_pkg",
                self._venv.site_pkgs,
                *pkg_args,
            ]
        )
        return self
