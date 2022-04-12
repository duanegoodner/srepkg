import subprocess
from pathlib import Path
from .srepkg_control_paths import HpkgControlPaths


class HpkgController:

    def __init__(self, safe_pkg_paths: HpkgControlPaths):
        self._paths = safe_pkg_paths

    @classmethod
    def for_env_builder(cls, safe_src: Path):
        return cls(HpkgControlPaths.for_env_builder(safe_src))

    @property
    def pkg_name(self):
        return self._paths.safe_src.name

    def inner_pkg_entry_point(self, entry_command: str, *pkg_args):
        subprocess.call([self._paths.venv_bin / entry_command, *pkg_args])
        return self

    def run_inner_pkg(self, *pkg_args):
        subprocess.call([self._paths.venv_py, '-m', self.pkg_name,
                         '--called_by_safe_pkg', self._paths.venv_pkg,
                         *pkg_args])
        return self
