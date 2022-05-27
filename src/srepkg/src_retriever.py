import shutil
import subprocess
import tarfile
import tempfile
import zipfile

from pathlib import Path


def id_pkg_source(pkg_ref: str):
    possible_src_types = {}

    if Path(pkg_ref).is_dir():
        possible_src_types['local'] = True


class SrcCodeRetriever:

    def __init__(self, pkg_ref: str, temp_dir: Path):
        self._pkg_ref = pkg_ref
        self._temp_dir = temp_dir

    def move_to_temp_dir(self):
        subprocess.call([
            'pip',
            'download',
            '-v',
            '--dest',
            str(self._temp_dir),
            self._pkg_ref,
            '--no-binary',
            ':all:',
            '--no-deps',
            '--no-use-pep517',
        ])

    @staticmethod
    def _uncompress(archive: Path, extract_dir: Path):

        if archive.suffix == '.zip':
            with zipfile.ZipFile(archive, 'r') as my_zip:
                my_zip.extractall(extract_dir)
        if archive.suffix == '.gz':
            with tarfile.open(archive) as my_tar:
                my_tar.extractall(extract_dir)

    def extract_and_install(self):
        archive_dir = tempfile.TemporaryDirectory()

        self.move_to_temp_dir()
        tempfile.TemporaryDirectory()



my_pkg_src_dir = Path.home() / 'srepkg_temp_dirs' / 'temp_dir'
if my_pkg_src_dir.exists():
    shutil.rmtree(my_pkg_src_dir)

my_src_code_retriever = SrcCodeRetriever(
    'howdoi', my_pkg_src_dir)
my_src_code_retriever.move_to_temp_dir()
#
# for file in my_src_code_retriever._temp_dir.iterdir():


my_src_code_retriever._uncompress()








