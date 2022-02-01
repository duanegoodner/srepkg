import argparse
import os
from pathlib import Path


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('orig_pkg_path')
    parser.add_argument('hpkg_path', nargs='?')
    return parser.parse_args()


def convert_to_path_objs(args):
    orig_pkg_path = Path(args.orig_pkg_path)
    if args.hpkg_path:
        dest_path = Path(args.hpkg_path)
    else:
        dest_path = Path(os.path.expanduser('~')) / 'hpackaged_pkgs' / \
                    (orig_pkg_path.name + '_hpkg')

    return orig_pkg_path, dest_path


def check_paths(orig_pkg_path, dest_path):

    if not orig_pkg_path.exists():
        print(str(orig_pkg_path), ' not found.')
        exit(1)
    if dest_path.exists():
        print(str(dest_path), ' already exists.')
        exit(1)
    if orig_pkg_path.is_relative_to(dest_path) or \
            dest_path.is_relative_to(orig_pkg_path):
        print('Building hpkg under same root as the original will cause too '
              'much confusion (at least in our opinion). Please choose'
              'different hpkg location.')
        exit(1)





