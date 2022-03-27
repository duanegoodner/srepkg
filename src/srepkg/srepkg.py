from srepkg.srepkg_builder import SrepkgBuilder
import srepkg.command_input as ci
import srepkg.orig_pkg_inspector as ipi
import srepkg.path_calculator as pc


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

    orig_pkg_info = ipi.OrigPkgInspector(args.orig_pkg_setup_dir)\
        .validate_orig_pkg_path()\
        .validate_setup_cfg()\
        .get_orig_pkg_info()

    builder_src_paths, builder_dest_paths = pc.BuilderPathsCalculator(
        orig_pkg_info, args.srepkg_name)\
        .calc_builder_paths()

    SrepkgBuilder(orig_pkg_info, builder_src_paths, builder_dest_paths)\
        .build_srepkg()


if __name__ == '__main__':
    main()
