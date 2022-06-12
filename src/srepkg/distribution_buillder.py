import os
import subprocess
import tempfile
import uuid
from pathlib import Path


class DistributionBuilder:

    # TODO setup logs with standard logging module
    # TODO handle case if archive already exists
    # TODO figure out why pkg_src param is a tuple
    def __init__(
            self,
            pkg_src: Path,
            archive_format: str,
            output_dir: Path,
            log_dir: Path
    ):

        self._pkg_src = pkg_src,
        self._archive_format = archive_format
        self._output_dir = output_dir
        self._log_dir = log_dir

    def _get_archive_fullname(self) -> str:
        assert Path.cwd().absolute() == self._pkg_src[0].absolute()

        fullname_file = tempfile.NamedTemporaryFile()

        with open(fullname_file.name, mode='w') as temp:
            subprocess.call(['python', 'setup.py', '--fullname'], stdout=temp)

        with open(fullname_file.name, mode='r') as temp:
            fullname = temp.readline().strip()

        return fullname

    def _build_archive_sdist(self, fullname: str):
        assert Path.cwd().absolute() == self._pkg_src[0].absolute()

        random_str = uuid.uuid4().hex
        log_path = self._log_dir / (random_str + fullname + '-log.txt')
        with log_path.open(mode='x') as log:
            subprocess.call([
                'python', 'setup.py', 'sdist', '-d', str(self._output_dir),
                '--quiet', '--formats=' + self._archive_format], stdout=log)
            print('Building source distribution of repackaged package')

    def write_archive(self):
        cwd = Path.cwd()

        try:
            os.chdir(str(self._pkg_src[0]))
            fullname = self._get_archive_fullname()
            self._build_archive_sdist(fullname)

        finally:
            os.chdir(str(cwd))

        archive_filename = fullname + '.' + self._archive_format

        return ''.join(archive_filename.split())
