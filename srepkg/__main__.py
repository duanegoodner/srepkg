"""
Entry point for the hpkg application. Command line syntax:
$ hpkg orig_pkg_path [hpkg_path]
"""

from srepkg.srepkg_builder import HpkgBuilder
import srepkg.srepkg_input as fsrpkg_input
import srepkg.path_calculator as pf


def main():
    """
    Builds a H-packaged version of existing packaged app.

    :param (from command line) orig_pkg_path = path of the package to be copied.
    :param (optional, from command line) hpkg_path = path to location where
    H-packaged version will be built. Default value is:
    ~/hpackaged_pkgs/<orig_pkg_name>_hpkg
    """
    args = fsrpkg_input.get_args()
    orig_pkg_path, dest_path = fsrpkg_input.convert_to_path_objs(args)
    src_paths, h_paths = pf.paths_builder(orig_pkg_path, dest_path)
    HpkgBuilder(src_paths, h_paths).build_hpkg()


if __name__ == '__main__':
    main()
