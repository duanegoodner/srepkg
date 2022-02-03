"""
Module for collecting / validating command line input and converting CL args to
Path objects.
"""

import argparse
import os
from pathlib import Path


def get_args():
    """
    Collects and parses command line args.
    :return: Namespace with orig_pkg_path and (if provided) hpkg_path
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('orig_pkg_path')
    parser.add_argument('hpkg_path', nargs='?')
    return parser.parse_args()


def check_paths(orig_pkg_path: Path, dest_path: Path):
    """
    Confirms that original package path exists, destination path does not yet
    exist, and that the (proposed) hpkg path is not a sub-path of the original.
    :param orig_pkg_path: Path object referencing original package
    :param dest_path: Path object
    """

    if not orig_pkg_path.exists():
        print(str(orig_pkg_path), ' not found.')
        exit(1)
    if dest_path.exists():
        print(str(dest_path), ' already exists.')
        exit(1)
    if orig_pkg_path.is_relative_to(dest_path) or \
            dest_path.is_relative_to(orig_pkg_path):
        print('Building hpkg under the original package root will cause too '
              'much confusion (at least in our opinion). Please choose'
              'different hpkg location.')
        exit(1)


def convert_to_path_objs(args):
    """
    Takes Namespace of path strings provided by argparser and converts to
    pathlib.Path objects
    :param args: Namespace of strings (from command line via argparser)
    :return: (orig_pkg_path, dest_path) tuple of Path objects
    """
    orig_pkg_path = Path(args.orig_pkg_path)
    if args.hpkg_path:
        dest_path = Path(args.hpkg_path)
    else:
        dest_path = Path(os.path.expanduser('~')) / 'hpackaged_pkgs' / \
                    (orig_pkg_path.name + '_hpkg_container') / \
                    (orig_pkg_path.name + '_hpkg')

    check_paths(orig_pkg_path, dest_path)

    return orig_pkg_path, dest_path







