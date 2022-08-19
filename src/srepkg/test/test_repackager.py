from pathlib import Path

import srepkg.repackager as rep
import srepkg.repackager_interfaces as rep_int
import srepkg.service_builder as sb


def test_repackager(tmp_path_factory):

    test_case_dir = Path(__file__).parent / 'package_test_cases'
    dist_out_dir = tmp_path_factory.mktemp("dist_out")
    construction_dir = tmp_path_factory.mktemp("construction_dir")

    srepkg_command = rep_int.SrepkgCommand(
        orig_pkg_ref=str(
            test_case_dir / 'wheel_inspect-1.7.1-py3-none-any.whl'),
        dist_out_dir=str(dist_out_dir),
        construction_dir=str(construction_dir)
    )

    service_class_builder = sb.ServiceBuilder(srepkg_command)
    repackager = rep.Repackager(
        srepkg_command=srepkg_command,
        service_class_builder=service_class_builder)

    repackager.repackage()

    output_suffixes = [item.suffix for item in list(dist_out_dir.iterdir())]
    assert '.whl' in output_suffixes
    assert '.zip' in output_suffixes
