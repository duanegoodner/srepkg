import argparse
import tempfile

import build
import hashlib
import subprocess
import sys
from pathlib import Path


class DistBuilder:

    def __init__(
            self,
            distribution: str,
            srcdir: Path,
            output_directory: Path,
            std_out_file: Path = tempfile.TemporaryFile(),
            std_err_file: Path = tempfile.TemporaryFile()):
        self._distribution = distribution
        self._srcdir = srcdir
        self._output_directory = output_directory
        self._std_out_file = std_out_file
        self._std_err_file = std_err_file

    @staticmethod
    def _calc_md5(file_path: Path):
        hash_md5 = hashlib.md5()
        with file_path.open(mode="rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def build(self):
        orig_dest_checksums = [self._calc_md5(item) for item in
                               self._output_directory.iterdir()]
        subprocess.run([sys.executable, __file__, self._distribution,
                        str(self._srcdir), str(self._output_directory)])

        new_files = [item for item in self._output_directory.iterdir() if
                     self._calc_md5(item) not in orig_dest_checksums]

        assert len(new_files) == 1

        return new_files[0]


class _DistBuilderArgParser:

    def __init__(self):
        self._parser = argparse.ArgumentParser()

    def _define_args(self):
        self._parser.add_argument("distribution", type=str)
        self._parser.add_argument("srcdir", type=str)
        self._parser.add_argument("output_directory", type=str)

    def get_args(self, *args):
        self._define_args()
        args_namespace = self._parser.parse_args(*args)
        return _DistBuilder(**vars(args_namespace))


class _DistBuilder:

    def __init__(self, distribution: str, srcdir: str, output_directory: str):
        self._distribution = distribution
        self._srcdir = srcdir
        self._output_directory = output_directory

    def build_dist(self) -> Path:
        dist_builder = build.ProjectBuilder(
            srcdir=self._srcdir,
            python_executable=sys.executable)

        dist_path_str = dist_builder.build(
            distribution=self._distribution,
            output_directory=self._output_directory)

        return Path(dist_path_str)


def main(*args):
    dist_builder = _DistBuilderArgParser().get_args(*args)
    dist_path = dist_builder.build_dist()


if __name__ == "__main__":
    main()
