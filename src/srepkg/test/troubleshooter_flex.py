from pathlib import Path
import srepkg.repackager_interfaces as rep_int
import srepkg.service_builder as sb
from srepkg.test.shared_fixtures import sample_pkgs


def test_build_from_src(sample_pkgs):

    test_case_dir = Path(
        '/Users/duane/dproj/srepkg/src/srepkg/test/package_test_cases')

    cur_command = rep_int.SrepkgCommand(
        orig_pkg_ref=sample_pkgs.numpy_py_pi,
        construction_dir='/Users/duane/srepkg_pkgs',
        dist_out_dir='/Users/duane/srepkg_pkgs'
    )

    service_builder = sb.ServiceBuilder(srepkg_command=cur_command)
    osp = service_builder.create_orig_src_preparer()

    construction_dir_summary = osp.prepare()

    srepkg_builder = service_builder.create_srepkg_builder(construction_dir_summary)

    # srepkg_builder._simple_construction_tasks()
    # srepkg_builder._build_entry_points()
    # srepkg_builder._write_srepkg_cfg_non_entry_data()
    # srepkg_builder._build_base_setup_cfg()
    #
    # srepkg_builder._srepkg_completers[1]._copy_ready_components()
    # srepkg_builder._srepkg_completers[1]._write_from_templates()
    # srepkg_builder._srepkg_completers[1]._write_srepkg_setup_cfg()
    # srepkg_builder._srepkg_completers[1]._extra_construction_tasks()
    # srepkg_builder._srepkg_completers[0]._install_inner_pkg()
    # srepkg_builder._srepkg_completers[1]._build_ipi_cfg()

    srepkg_builder.build()


# if __name__ == '__main__':
#     test_build_from_src()
