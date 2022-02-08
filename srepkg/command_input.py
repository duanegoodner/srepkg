"""
Module for collecting command line input.
"""

import argparse


def get_args():
    """
    Collects and parses command line args.

    Expected command line syntax:
    $ python_interpreter -m srepkg orig_pkg_path [srepkg_path]

    :return: Namespace with orig_pkg_path and (if provided) srepkg_path
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('orig_pkg_path')
    parser.add_argument('hpkg_path', nargs='?')
    return parser.parse_args()







