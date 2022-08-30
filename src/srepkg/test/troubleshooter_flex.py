from pathlib import Path
import srepkg.repackager_interfaces as rep_int
import srepkg.service_builder as sb


def test_build_from_src():

    test_case_dir = Path(
        '/Users/duane/dproj/srepkg/src/srepkg/test/package_test_cases')

    cur_command = rep_int.SrepkgCommand(
        orig_pkg_ref=str(test_case_dir / 'testproj'),
        construction_dir='/Users/duane/srepkg_pkgs',
        dist_out_dir='/Users/duane/srepkg_pkgs'
    )

    service_builder = sb.ServiceBuilder(srepkg_command=cur_command)
    osp = service_builder.create_orig_src_preparer()

    construction_dir_summary = osp.prepare()

    srepkg_builder = service_builder.create_srepkg_builder(construction_dir_summary)
    # assert len(srepkg_builder._srepkg_completers) == 2
    # srepkg_builder.build()

    # srepkg_builder._srepkg_completers[0]._adjust_base_pkg()
    # srepkg_builder._srepkg_completers[0]._build_srepkg_dist()
    # srepkg_builder._srepkg_completers[0]\
    #     .build_and_cleanup(Path('/Users/duane/srepkg_pkgs'))
    srepkg_builder._simple_construction_tasks()
    srepkg_builder._build_entry_points()
    srepkg_builder._write_srepkg_cfg_non_entry_data()
    srepkg_builder._build_base_setup_cfg()

    srepkg_builder._srepkg_completers[1]._simple_copy_ops()
    srepkg_builder._srepkg_completers[1]._build_manifest()
    srepkg_builder._srepkg_completers[1]._build_srepkg_cfg()


    # srepkg_builder._srepkg_completers[1]._adjust_base_pkg()
    # srepkg_builder._srepkg_completers[1].build_and_cleanup()
    # srepkg_builder.build()


if __name__ == '__main__':
    test_build_from_src()
