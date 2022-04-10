"""
Module for collecting command line input.
"""

import argparse


def get_args(*args):
    """
    Collects and parses command line args.

    Expected command line syntax:
    $ python_interpreter -m srepkg orig_pkg_path [srepkg_name]

    :return: Namespace with orig_pkg_path and (if provided) srepkg_name
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'orig_pkg_path',
        type=str,
        help="Path to directory containing original package's setup.cfg file")

    parser.add_argument(
        '--srepkg_name',
        type=str,
        nargs='?',
        action='store',
        help="Name to be used for repackaged package. "
             "Default is <original-pkg-name-from-setup.cfg + 'srepkg'>"
    )
    return parser.parse_args(*args)
