import argparse
import srepkg.error_handling.custom_exceptions as ce
import srepkg.repackager_interfaces as rep_int



class SrepkgCommandLine(rep_int.SrepkgCommandInterface):

    def __init__(self):
        self._parser = argparse.ArgumentParser()

    def _attach_args(self):
        self._parser.add_argument(
            "orig_pkg_ref",
            type=str,
            help="A reference to the original package to be repackaged. Can "
                 "be a local path to a directory where a package's setup.py "
                 "resides, a  PyPI package name, or Github repo",
        )

        self._parser.add_argument(
            "-g",
            "--git_commit_ref",
            type=str,
            nargs="?",
            action="store",
            help="A reference to a git commit to be used. Can either be a "
                 "branch name, or a commit SHA. Defaults to: HEAD of the "
                 "default branch for a remote Github repository; the currently"
                 " checked out branch for a local repository. Providing "
                 "GIT COMMIT_REF and ORIG_PKG_VERSION args in the same "
                 "command causes an exception to be raised."
        )

        self._parser.add_argument(
            "-r",
            "--orig_pkg_version",
            type=str,
            nargs="?",
            action="store",
            help="Original package version. For use with git repos (local or "
                 "remote), and PyPI package refs. Providing GIT COMMIT_REF and "
                 "ORIG_PKG_VERSION args in the same command causes an "
                 "exception to be raised."
        )

        self._parser.add_argument(
            "-n",
            "--srepkg_name",
            type=str,
            nargs="?",
            action="store",
            help="Name to be used for repackaged package. Default is "
                 "<ORIGINAL_PACKAGE_NAME + srepkg>",
        )

        self._parser.add_argument(
            "-c",
            "--construction_dir",
            type=str,
            nargs="?",
            action="store",
            help="Directory where non-compressed repackage will be built and "
                 "saved. If not specified, srepkg is built in a temp "
                 "directory and deleted after distribution archive creation",
        )

        self._parser.add_argument(
            "-d",
            "--dist_out_dir",
            type=str,
            nargs="?",
            action="store",
            help="Directory where srepkg distribution .zip file is saved. "
                 "Default is the current working directory.",
        )

    def get_args(self, *args) -> rep_int.SrepkgCommand:
        self._attach_args()
        args_namespace = self._parser.parse_args(*args)
        if args_namespace.git_commit_ref and args_namespace.orig_pkg_version:
            raise ce.PkgVersionWithCommitRef(
                commit_ref=args_namespace.commit_ref,
                pkg_version=args_namespace.orig_pkg_version)
        return rep_int.SrepkgCommand(**vars(args_namespace))
