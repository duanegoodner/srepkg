import tempfile
from pathlib import Path
import srepkg.command_input as ci
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
    re.Repackager(
        pkg_ref=args.pkg_ref,
        srepkg_name=args.srepkg_name,
        srepkg_location=args.srepkg_location
    ).repackage()


if __name__ == '__main__':
    main()
