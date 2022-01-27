import os
from subprocess import call
from safe_pkg_paths import SafePkgPaths


class SafePkgController:

    def __init__(self, safe_pkg_paths: SafePkgPaths):
        self._paths = safe_pkg_paths
        self._pkg_name = os.path.basename(self._paths.safe_src)

    def install_utilities(self, *utility_packages):
        call([self._paths.venv_pip, 'install', *utility_packages])
        return self

    def install_inner_pkg(self):
        call([self._paths.venv_pip, 'install',
              os.path.dirname(self._paths.safe_src) + '/.'])
        return self

    def run_inner_pkg(self, *pkg_args):
        call([self._paths.venv_py, '-m', self._pkg_name,
              '--called_by_safe_pkg', self._paths.venv_pkg, *pkg_args])
        return self
