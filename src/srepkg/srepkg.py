# import srepkg.srepkg_builder as sb
import srepkg.command_input as ci
# import srepkg.orig_pkg_inspector as opi
# import srepkg.path_calculator as pc

import srepkg.repackager as re


def main():
    """
    Builds 'Solo Re-Packaged' (srepkg) version of existing packaged app.
    Command line syntax is:
    $ python_interpreter_path srepkg -m orig_pkg_path [srepkg_name]

    Default value of srepkg_name is: <orig_pkg_name>sr
    'orig_pkg_name' is the basename of orig_pkg_path (and the name of
    the original package)

    SRE-packaged version is saved in:
     ~/srepkg_pkgs/<orig_pkg_name>_srepkg/<srepkg_name>
    """
    args = ci.get_args()
    re.repackage(orig_pkg_path=args.orig_pkg_path, srepkg_name=args.srepkg_name)


if __name__ == '__main__':
    main()
