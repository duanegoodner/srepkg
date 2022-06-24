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
        "orig_pkg_ref",
        type=str,
        help="A reference to the original package to be repackaged. Can be a "
        "local path to a directory where a package's setup.py resides, a"
        " PyPI package name, or Github repo",
    )

    parser.add_argument(
        "-n",
        "--srepkg_name",
        type=str,
        nargs="?",
        action="store",
        help="Name to be used for repackaged package. Default is "
        "<ORIGINAL_PACKAGE_NAME + srepkg>",
    )

    parser.add_argument(
        "-c",
        "--construction_dir",
        type=str,
        nargs="?",
        action="store",
        help="Directory where non-compressed repackage will be built and "
        "saved. If not specified, srepkg is built in a temp directory and"
        " deleted after distribution archive creation",
    )

    parser.add_argument(
        "-d",
        "--dist_out_dir",
        type=str,
        nargs="?",
        action="store",
        help="Directory where srepkg distribution .zip file is saved. Default "
        "is the current working directory.",
    )

    return parser.parse_args(*args)
