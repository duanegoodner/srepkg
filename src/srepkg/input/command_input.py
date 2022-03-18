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
    parser.add_argument('orig_pkg')

    parser.add_argument('srepkg_name', nargs='?')
    return parser.parse_args(*args)
