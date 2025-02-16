"""
Contains class for retrieving arguments from command line.
"""

import argparse
from pathlib import Path
import srepkg.error_handling.custom_exceptions as ce
import srepkg.repackager_interfaces as rep_int


class SrepkgCommandLine(rep_int.SrepkgCommandInterface):
    """
    Retrieves arguments from command line.
    """
    def __init__(self):
        self._parser = argparse.ArgumentParser()

    def _attach_args(self):
        """
        Attaches command line arguments to parser.

        Returns:
            None
        """
        self._parser.add_argument(
            "orig_pkg_ref",
            type=str,
            help="A reference to the original package to be repackaged. Can "
            "be a local path to the directory where a package's setup.py "
            "or pyproject.toml resides, a  PyPI package name, or a Github"
            " repo url.",
        )

        self._parser.add_argument(
            "-g",
            "--git_ref",
            type=str,
            nargs="?",
            action="store",
            help="A git branch name, tag name, or commit SHA that determines "
            "the original package commit to use (if ORIG_PKG_REF is a "
            "git repo). Defaults to: HEAD of the default branch for a "
            "remote Github repo, and the currently checked out branch "
            "for a local repo.",
        )

        self._parser.add_argument(
            "-r",
            "--pypi_version",
            type=str,
            nargs="?",
            action="store",
            help="Original package version to use (if ORIG_PKG_REF is a PyPI"
            " package). Defaults to the latest PyPI package.",
        )

        self._parser.add_argument(
            "-n",
            "--srepkg_name",
            type=str,
            nargs="?",
            action="store",
            help="Name to be used for repackaged package. Default is "
            "<{ORIGINAL_PACKAGE_NAME}srepkg>",
        )

        self._parser.add_argument(
            "-c",
            "--construction_dir",
            type=str,
            nargs="?",
            action="store",
            help="Directory where non-compressed repackage will be built and "
            "saved. If not specified, srepkg is built in a temp "
            "directory that gets deleted after wheel and or sdist archives"
            "have been created.",
        )

        self._parser.add_argument(
            "-d",
            "--dist_out_dir",
            type=str,
            nargs="?",
            action="store",
            help="Directory where srepkg wheel and or sdist archives are "
            "saved. Default is under relative path ./srepkg_dist which "
                 "gets created if it does not already exist.",
        )

        self._parser.add_argument(
            "-f",
            "--logfile_dir",
            type=str,
            nargs="?",
            action="store",
            help="Directory to write srepkg log file to. Default behavior is "
            "to write log to file in temporary directory that is "
            "automatically deleted at end of execution.",
        )

    # TODO: Place / call as much downstream logic as possible for setting
    #  defaults to this method. Some can't go here b/c determination can
    #  only be made downstream.
    @staticmethod
    def _set_defaults(args_namespace: argparse.Namespace):
        """
        Sets default values for command line arguments.

        Args:
            args_namespace (): key-value pairs collected from the command
            line args.

        Returns:
            None

        """
                
        if args_namespace.dist_out_dir is None:
            args_namespace.dist_out_dir = Path.cwd() / "srepkg_dists"
        
    
    def get_args(self, *args) -> rep_int.SrepkgCommand:
        """
        Collects command line arguments and converts to SrepkgCommand used
        by downstream classes.
        Args:
            *args (): Entry point arguments, typically from command line.

        Returns:
            a SrepkgCommand instance

        """
        self._attach_args()
        args_namespace = self._parser.parse_args(*args)
        self._set_defaults(args_namespace=args_namespace)
        if args_namespace.git_ref and args_namespace.pypi_version:
            raise ce.PkgVersionWithCommitRef(
                commit_ref=args_namespace.git_ref,
                pkg_version=args_namespace.pypi_version,
            )

        return rep_int.SrepkgCommand(**vars(args_namespace))
