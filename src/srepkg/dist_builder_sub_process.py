import argparse
import build
import sys
from pathlib import Path


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