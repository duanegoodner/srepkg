import venv
import subprocess
from pathlib import Path
from types import SimpleNamespace

import custom_datatypes.named_tuples as nt


class NewVenvManager:
    def __init__(self, venv_context: SimpleNamespace):
        self._venv_context = venv_context

    def install_pkg(self, pkg_ref: str):
        subprocess.call([
            self._venv_context.env_exe, '-m', 'pip', 'install', pkg_ref])


class VenvManager:

    def __init__(self, root: Path):
        self._root = root
        self._orig_pkg_info = orig_pkg_info
        self._srepkg_path = srepkg_path

    @property
    def _venv_path(self):
        return self._srepkg_path / (self._orig_pkg_info.pkg_name + '_venv')

    @property
    def _py(self):
        return self._root / 'bin' / 'python'

    @property
    def _pip(self):
        return self._root / 'bin' / 'pip'

    def _upgrade_pip(self):
        subprocess.call([self._py, '-m', 'pip', 'install',
                         '--upgrade', 'pip'])
        return self

    def _install_utilities(self, *utility_packages):
        subprocess.call([self._pip, 'install', *utility_packages])

        return self

    def initialize_venv(self):
        env_builder = venv.EnvBuilder(with_pip=True)
        env_builder.create(self._root)

        self._upgrade_pip()._install_utilities('wheel')

    def _install_pkg(self, pkg_ref: str):
        subprocess.call([self._pip, 'install', pkg_ref, '--quiet'])

        return self

    # def build_venv_with_orig_pkg(self):
    #     self._build_venv()\
    #         ._upgrade_pip()\
    #         ._install_utilities('wheel')\
    #         ._install_inner_pkg()


class DistInfoExtractor:

    def __init__(self, pkg_name: str, venv_path: Path):
        self._pkg_name = pkg_name
        self._venv_path = venv_path





