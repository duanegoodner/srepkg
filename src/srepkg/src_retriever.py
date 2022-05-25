import shutil
import subprocess

from pathlib import Path


class SrcCodeRetriever:

    def __init__(self, pkg_ref: str, temp_dir: Path):
        self._pkg_ref = pkg_ref
        self._temp_dir = temp_dir

    def move_to_temp_dir(self):
        subprocess.call([
            'pip',
            'download',
            '--dest',
            str(self._temp_dir),
            self._pkg_ref,
            '--no-binary',
            ':all:',
            '--no-deps',
            '--no-use-pep517',
        ])


my_pkg_src_dir = Path.home() / 'srepkg_temp_dirs' / 'howdoi'
if my_pkg_src_dir.exists():
    shutil.rmtree(my_pkg_src_dir)

my_src_code_retriever = SrcCodeRetriever(
    '/Users/duane/dproj/srepkg', my_pkg_src_dir)
my_src_code_retriever.move_to_temp_dir()








