from pathlib import Path

import srepkg.service_builder as sb
import srepkg.shared_data_structures.new_data_structures as nds


def test_build_from_src():

    test_case_dir = Path(
        '/Users/duane/dproj/srepkg/src/srepkg/test/package_test_cases')

    cur_command = nds.SrepkgCommand(
        orig_pkg_ref=str(test_case_dir / 'testproj-0.0.0.tar.gz'),
        construction_dir='/Users/duane/srepkg_pkgs')

    service_builder = sb.ServiceBuilder(srepkg_command=cur_command)
    osp = service_builder.create_orig_src_preparer()
    osp.prepare()
    srepkg_builder = service_builder.create_srepkg_builder()
    srepkg_builder.build()

    # srepkg_builder._srepkg_completers[0]._adjust_base_pkg()
    # srepkg_builder._srepkg_completers[0]._build_srepkg_dist()
    srepkg_builder._srepkg_completers[0].build_and_cleanup()