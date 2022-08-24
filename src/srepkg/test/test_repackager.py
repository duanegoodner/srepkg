from pathlib import Path
import srepkg.srepkg_builder as s_bldr
import srepkg.repackager as rep
import srepkg.repackager_interfaces as rep_int
import srepkg.service_builder as sb
from srepkg.test.shared_fixtures import sample_pkgs


def test_repackager(mocker, tmp_path_factory, sample_pkgs):

    dist_out_dir = tmp_path_factory.mktemp("dist_out")
    construction_dir = tmp_path_factory.mktemp("construction_dir")

    srepkg_command = rep_int.SrepkgCommand(
        orig_pkg_ref=sample_pkgs.wheel_inspect_whl,
        dist_out_dir=str(dist_out_dir),
        # construction_dir=str(construction_dir)
    )

    service_class_builder = sb.ServiceBuilder(srepkg_command)
    repackager = rep.Repackager(
        srepkg_command=srepkg_command,
        service_class_builder=service_class_builder)

    mocker.patch.object(s_bldr.SrepkgBuilder, "build", return_value=None)

    repackager.repackage()



    # output_suffixes = [item.suffix for item in list(dist_out_dir.iterdir())]
    # assert '.whl' in output_suffixes
    # assert '.zip' in output_suffixes
