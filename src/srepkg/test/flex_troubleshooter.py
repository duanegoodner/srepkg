from pathlib import Path
import srepkg.repackager_interfaces as rep_int
import srepkg.service_builder as sb


def test_build_from_src(tmp_path):

    test_case_dir = Path(
        '/Users/duane/dproj/srepkg/src/srepkg/test/package_test_cases')

    cur_command = rep_int.SrepkgCommand(
        orig_pkg_ref=str(test_case_dir / 'wheel_inspect-1.7.1-py3-none-any.whl'),
        construction_dir='/Users/duane/srepkg_pkgs')

    service_builder = sb.ServiceBuilder(srepkg_command=cur_command)
    osp = service_builder.create_orig_src_preparer()
    assert type(osp._provider).__name__ == 'DistCopyProvider'
    assert type(osp._receiver).__name__ == 'CustomConstructionDir'
    assert type(osp._retriever).__name__ == 'NullPkgRetriever'

    osp.prepare()

    srepkg_builder = service_builder.create_srepkg_builder()
    assert len(srepkg_builder._srepkg_completers) == 2
    srepkg_builder.build()

    # srepkg_builder._srepkg_completers[0]._adjust_base_pkg()
    # srepkg_builder._srepkg_completers[0]._build_srepkg_dist()
    srepkg_builder._srepkg_completers[0]\
        .build_and_cleanup(Path('/Users/duane/srepkg_pkgs'))

    # srepkg_builder._srepkg_completers[1]._adjust_base_pkg()
    # srepkg_builder._srepkg_completers[1].build_and_cleanup()


if __name__ == '__main__':
    test_build_from_src()
