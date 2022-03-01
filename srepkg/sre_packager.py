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


    orig_pkg_path, dest_path = pc.calc_root_paths_from(args)
    pc.validate_root_paths(orig_pkg_path, dest_path)
    pc.validate_orig_pkg(orig_pkg_path)
    orig_pkg_info = pc.read_orig_pkg_info(orig_pkg_path)

    src_paths, h_paths = pc.create_builder_paths(orig_pkg_path, dest_path)
    SrepkgBuilder(orig_pkg_info, src_paths, h_paths).build_srepkg()


if __name__ == '__main__':
    main()
