from hpkg.builder.hpkg_builder import HpkgBuilder
import hpkg.input.hpkg_input as hpkg_input


def main():
    args = hpkg_input.get_args()
    orig_pkg_path, dest_path = hpkg_input.convert_to_path_objs(args)
    hpkg_input.check_paths(orig_pkg_path, dest_path)
    hpkg_builder = HpkgBuilder(orig_pkg_path, dest_path)
    hpkg_builder.build_hpkg()


if __name__ == '__main__':
    main()
