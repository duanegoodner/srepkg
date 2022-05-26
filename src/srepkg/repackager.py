import srepkg.orig_pkg_inspector as opi
import srepkg.path_calculator as pc
import srepkg.srepkg_builder as sb


def repackage(orig_pkg_path: str, srepkg_name: str):

    orig_pkg_info = opi.OrigPkgInspector(orig_pkg_path).get_orig_pkg_info()

    builder_src_paths, builder_dest_paths = pc.BuilderPathsCalculator(
        orig_pkg_info, srepkg_name).calc_builder_paths()

    sb.SrepkgBuilder(orig_pkg_info, builder_src_paths,
                     builder_dest_paths).build_srepkg()

