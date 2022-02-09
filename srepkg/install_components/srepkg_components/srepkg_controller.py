import shutil
import subprocess
import venv
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

    def build_venv(self):
        env_builder = venv.EnvBuilder(with_pip=True)
        env_builder.create(self._paths.safe_src.parent.absolute().joinpath(
            str(self._paths.safe_src.name + '_venv')))
        return self

    def upgrade_pip(self):
        subprocess.call([self._paths.venv_py, '-m', 'pip', 'install',
                         '--upgrade', 'pip', '--quiet'])
        return self

    def install_utilities(self, *utility_packages):
        subprocess.call([self._paths.venv_pip, 'install', *utility_packages,
                         '--quiet'])
        return self

    def install_inner_pkg(self):
        (self._paths.safe_src.parent / 'setup_off.py').rename(
            self._paths.safe_src.parent / 'setup.py')
        subprocess.call([self._paths.venv_pip, 'install',
                         self._paths.safe_src.parent / '.', '--quiet'])
        (self._paths.safe_src.parent / 'setup.py').rename(
            self._paths.safe_src.parent / 'setup_off.py')
        return self

    def run_inner_pkg(self, *pkg_args):
        subprocess.call([self._paths.venv_py, '-m', self.pkg_name,
                         '--called_by_safe_pkg', self._paths.venv_pkg,
                         *pkg_args])
        return self
