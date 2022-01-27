import os
from subprocess import call
from shutil import copytree, ignore_patterns
import venv
from enums import ReqSource

files_to_remove = ['.git', '.gitignore', '.idea']


def init_safe_pkg_shell(safe_pkg_path: str):
    with open(safe_pkg_path + '/__init__.py', 'w') as init_file:
        pass


def copy_package(orig_pkg_path: str, safe_pkg_path: str):
    copy_location = copytree(orig_pkg_path, safe_pkg_path, ignore=ignore_patterns('*.git', '*.gitignore', '*.idea'))


def build_package_venv(pkg_root: str, install_pkg: bool, req_source: ReqSource = ReqSource.NONE):
    env_builder = venv.EnvBuilder(with_pip=True)
    venv_dir = pkg_root + '/venv'
    env_builder.create(venv_dir)

    if install_pkg:
        call([venv_dir + '/bin/pip', 'install', pkg_root + '/.'])

    return venv_dir


class SafePkg:
    env_builder = venv.EnvBuilder(with_pip=True)

    def __init__(self, orig_pkg_path: str, safe_pkg_path: str):
        copy_results = copytree(orig_pkg_path, safe_pkg_path, ignore=ignore_patterns('*.git', '*.gitignore', '*.idea',
                                                                                     '*.__pycache__'))
        self.env_builder.create(safe_pkg_path + '/venv')
        self._orig_path = orig_pkg_path
        self._safe_path = safe_pkg_path


# copy_package('/Users/duane/dproj/xiangqigame', '/Users/duane/dproj/safe_xiangqigame')
init_safe_pkg_shell('/Users/duane/dproj/safe_xiangqigame')



# safe_xiangqi_game = SafePkg('/Users/duane/dproj/xiangqigame', '/Users/duane/dproj/safe_repkg/safe_xiangqigame')
# build_package_venv(pkg_root='/Users/duane/dproj/safe_repkg/safe_xiangqigame', install_pkg=True)
