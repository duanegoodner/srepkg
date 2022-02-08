"""
Entry point for the srepkg application. Command line syntax:
$ python_interpreter_path srepkg -m orig_pkg_path [srepkg_path]
"""

from srepkg.srepkg_builder import SrepkgBuilder
import srepkg.command_input as ci
import srepkg.path_calculator as pc


def main():
    """
    Builds 'Solo Re-Packaged' (srepkg)  version of existing packaged app.

    :param (from command line) orig_pkg_path = path of the package to be copied.
    :param (optional, from command line) srepkg_path = path to location where
    sre-packaged version will be built. Default value is:
    ~/srepkgs/<orig_pkg_name>srepkg
    """
    args = ci.get_args()
    orig_pkg_path, dest_path = pc.calc_root_paths_from(args)
    src_paths, h_paths = pc.create_builder_paths(orig_pkg_path, dest_path)
    SrepkgBuilder(src_paths, h_paths).build_srepkg()


if __name__ == '__main__':
    main()
