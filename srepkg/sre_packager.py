from srepkg.srepkg_builder import SrepkgBuilder
import srepkg.command_input as ci
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

    path_calculator = pc.PathCalculator(args)
    path_calculator.validate_orig_pkg_path()
    path_calculator.validate_setup_cfg()
    orig_pkg_info = path_calculator.get_orig_cfg_info()

    dest_paths = path_calculator.build_dest_paths(orig_pkg_info)

    SrepkgBuilder(
        orig_pkg_info,
        path_calculator.builder_src_paths,
        dest_paths
    ).build_srepkg()


if __name__ == '__main__':
    main()
