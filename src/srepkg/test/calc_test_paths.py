import srepkg.test.persistent_locals as p_loc
import srepkg.command_input as ci
import srepkg.test.t_proj.t_proj_info as tpi
import srepkg.orig_pkg_inspector as opi
import srepkg.path_calculator as pc
import srepkg.test.t_proj_srepkg_info as tpsi


@p_loc.PersistentLocals
def calc_test_paths():
    args = ci.get_args([str(tpi.pkg_root)])

    orig_pkg_info = opi.OrigPkgInspector(args.orig_pkg_setup_dir) \
        .validate_orig_pkg_path() \
        .validate_setup_cfg() \
        .get_orig_pkg_info()

    builder_paths_calculator = pc.BuilderPathsCalculator(
        orig_pkg_info, args.srepkg_name)

    # use non-standard path for srepkgs_pkgs to avoid unwanted overwrite
    builder_paths_calculator.srepkg_pkgs_dir = tpsi.test_srepkg_pkgs_dir

    builder_src_paths, builder_dest_paths =\
        builder_paths_calculator.calc_builder_paths()

    return builder_src_paths, builder_dest_paths
