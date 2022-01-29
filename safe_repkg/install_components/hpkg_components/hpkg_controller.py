import os
import shutil
from subprocess import call
from .hpkg_paths import HpkgPaths


class HpkgController:

    def __init__(self, safe_pkg_paths: HpkgPaths):
        self._paths = safe_pkg_paths
        self._pkg_name = os.path.basename(self._paths.safe_src)
        self._junk_dirs = [
            '/build',
            '/' + self._pkg_name + '.egg-info'
        ]

    @classmethod
    def for_env_builder(cls, safe_src: str):
        return cls(HpkgPaths.for_env_builder(safe_src))

    def upgrade_pip(self):
        print([self._paths.venv_py, '-m', self._paths.venv_pip, 'install',
              '--upgrade', 'pip'])
        call([self._paths.venv_py, '-m', 'pip', 'install',
              '--upgrade', 'pip'])
        return self

    def install_utilities(self, *utility_packages):
        call([self._paths.venv_pip, 'install', *utility_packages])
        return self

    def install_inner_pkg(self):
        print(self._paths.safe_src)
        call([self._paths.venv_pip, 'install', '.'])
        return self

    def remove_unwanted_dir(self, dir_path):
        try:
            shutil.rmtree(dir_path)
        except (OSError, FileNotFoundError) as e:
            pass
        return self

    def post_install_cleanup(self):
        for base_name in self._junk_dirs:
            self.remove_unwanted_dir(os.path.dirname(self._paths.safe_src)
                                     + base_name )
        return self

    def run_inner_pkg(self, *pkg_args):
        os.chdir(os.path.dirname(self._paths.venv_pkg))
        call([self._paths.venv_py, '-m', self._pkg_name,
              '--called_by_safe_pkg', self._paths.safe_src, *pkg_args])
        return self
