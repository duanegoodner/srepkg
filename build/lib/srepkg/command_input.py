"""
Module for collecting command line input.
"""

import argparse


def get_args(*args):
    """
    Collects and parses command line args.
    usage: srepkg [-h] [--srepkg_name [SREPKG_NAME]] orig_pkg_path

    :return: Namespace with orig_pkg_path and (if provided) srepkg_name
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'pkg_ref',
        type=str,
        help="Original package to be repackaged. Can be a local path, PyPI "
             "package name, or Github repo.")

    parser.add_argument(
        '--srepkg_name',
        type=str,
        nargs='?',
        action='store',
        help="Custom name to be used for repackaged package."
    )

    parser.add_argument(
        '--srepkg_location',
        type=str,
        nargs='?',
        action='store',
        help='Directory where srepkg will be saved. Default is ~/srepkg_pkgs.'
    )
    return parser.parse_args(*args)
