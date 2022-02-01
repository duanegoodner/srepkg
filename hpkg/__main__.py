import argparse
import os
from pathlib import Path
from .hpkg_builder import HpkgBuilder


parser = argparse.ArgumentParser()
parser.add_argument('orig_pkg_path')
parser.add_argument('hpkg_path', nargs='?')
args = parser.parse_args()


if __name__ == '__main__':
    orig_pkg_path = Path(args.orig_pkg_path)
    if args.hpkg_path:
        dest_path = Path(args.hpkg_path)
    else:
        dest_path = Path(os.path.expanduser('~')) / 'hpackaged_pkgs' / \
                    (orig_pkg_path.name + '_hpkg')

    hpkg_builder = HpkgBuilder(orig_pkg_path, dest_path)
    hpkg_builder.build_hpkg()
