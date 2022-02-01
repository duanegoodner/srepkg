import argparse
from pathlib import Path
from .hpkg_builder import HpkgBuilder


parser = argparse.ArgumentParser()
parser.add_argument('orig_pkg_path')
parser.add_argument('hpkg_path')
args = parser.parse_args()


if __name__ == '__main__':
    hpkg_builder = HpkgBuilder(Path(args.orig_pkg_path), Path(args.hpkg_path))
    hpkg_builder.build_hpkg()
