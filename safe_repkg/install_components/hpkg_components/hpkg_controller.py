import shutil
import subprocess
import venv
from pathlib import Path
from .hpkg_paths import HpkgPaths


class HpkgController:

    def __init__(self, safe_pkg_paths: HpkgPaths):
        self._paths = safe_pkg_paths
        self._pkg_name = self._paths.safe_src.name
        self._remove_patterns = [
            '/build',
            '/' + self._pkg_name + '.egg-info'
        ]

    @classmethod
    def for_env_builder(cls, safe_src: Path):
        return cls(HpkgPaths.for_env_builder(safe_src))

    def build_venv(self):
        env_builder = venv.EnvBuilder(with_pip=True)
        env_builder.create(self._paths.safe_src.parent.absolute().joinpath(
            str(self._paths.safe_src.name + '_venv')))
        return self

    def upgrade_pip(self):
        subprocess.call([self._paths.venv_py, '-m', 'pip', 'install',
                         '--upgrade', 'pip'])
        return self

    def install_utilities(self, *utility_packages):
        subprocess.call([self._paths.venv_pip, 'install', *utility_packages])
        return self

    def install_inner_pkg(self):
        subprocess.call([self._paths.venv_pip, 'install', '.'])
        return self

    def remove_unwanted_dir(self, dir_path):
        try:
            shutil.rmtree(dir_path)
        except (OSError, FileNotFoundError) as e:
            pass
        return self

    def post_install_cleanup(self):
        for base_name in self._remove_patterns:
            self.remove_unwanted_dir(self._paths.safe_src / base_name)
        return self

    def run_inner_pkg(self, *pkg_args):
        subprocess.call([self._paths.venv_py, '-m', self._pkg_name,
                         '--called_by_safe_pkg', self._paths.safe_src,
                         *pkg_args])
        return self
