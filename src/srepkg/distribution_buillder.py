import os
import subprocess
import tempfile
from pathlib import Path


class DistributionBuilder:

    # TODO setup logs with standard logging module
    # TODO handle case if archive already exists
    # TODO figure out why pkg_src is a tuple even though Path passes as arg
    def __init__(self, pkg_src: Path, archive_format: str, output_dir: Path):

        self._pkg_src = pkg_src
        self._archive_format = archive_format
        self._output_dir = output_dir

    def _get_archive_fullname(self) -> str:
        assert Path.cwd() == self._pkg_src

        fullname_file = tempfile.NamedTemporaryFile()

        with open(fullname_file.name, mode='w') as temp:
            subprocess.call(['python', 'setup.py', '--fullname'], stdout=temp)

        with open(fullname_file.name, mode='r') as temp:
            fullname = temp.readline().strip()

        return fullname

    def _build_archive_sdist(self):
        assert Path.cwd() == self._pkg_src

        log_path = tempfile.NamedTemporaryFile()
        with open(log_path.name, mode='w') as logfile:
            subprocess.call([
                'python', 'setup.py', 'sdist', '-d', str(self._output_dir),
                '--quiet', '--formats=' + self._archive_format], stdout=logfile)
            print('Building source distribution of repackaged package')

    def write_archive(self):
        cwd = Path.cwd()

        try:
            os.chdir(str(self._pkg_src))
            fullname = self._get_archive_fullname()
            self._build_archive_sdist()

        finally:
            os.chdir(str(cwd))

        archive_filename = fullname + '.' + self._archive_format

        return ''.join(archive_filename.split())
