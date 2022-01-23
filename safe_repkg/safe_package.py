import os
from subprocess import call
from shutil import copytree, ignore_patterns


files_to_remove = ['.git', '.gitignore', '.idea']


class SafePkg:

    def __init__(self, orig_pkg_path: str, safe_pkg_path: str):

        copytree(orig_pkg_path, safe_pkg_path, ignore=ignore_patterns('*.git', '*.gitignore', '*.idea'))
        self._orig_path = orig_pkg_path
        self._safe_path = safe_pkg_path


safe_xiangqi_game = SafePkg('/Users/duane/dproj/xiangqi_game', '/Users/duane/dproj/safe_repkg/safe_xiangqi_game')


