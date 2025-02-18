import argparse
import build
import sys
from pathlib import Path


class _DistBuilderArgParser:

    def __init__(self):
        self._parser = argparse.ArgumentParser()

    def _define_args(self):
        self._parser.add_argument("distribution", type=str)
        self._parser.add_argument("source_dir", type=str)
        self._parser.add_argument("output_directory", type=str)

    def get_args(self, *args):
        self._define_args()
        args_namespace = self._parser.parse_args(*args)
        return _DistBuilder(**vars(args_namespace))


class _DistBuilder:

    def __init__(self, distribution: str, source_dir: str, output_directory: str):
        self._distribution = distribution
        self._source_dir = source_dir
        self._output_directory = output_directory

    def build_dist(self) -> Path:
        dist_builder = build.ProjectBuilder(
            source_dir=self._source_dir, python_executable=sys.executable
        )

        dist_path_str = dist_builder.build(
            distribution=self._distribution,
            output_directory=self._output_directory,
        )

        return Path(dist_path_str)


def main(*args) -> Path:
    dist_builder = _DistBuilderArgParser().get_args(*args)
    dist_path = dist_builder.build_dist()
    return dist_path


if __name__ == "__main__":
    main()
