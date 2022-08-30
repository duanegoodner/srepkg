import unittest.mock as mock
from pathlib import Path

import srepkg.repackager as rep
import srepkg.repackager_interfaces as rep_int
import srepkg.service_builder as sb
import srepkg.srepkg_builder as s_bldr

from srepkg.test.shared_fixtures import sample_pkgs


def test_repackager(tmp_path_factory, sample_pkgs):
    dist_out_dir = Path("/Users/duane/srepkg_pkgs")
    construction_dir = Path("/Users/duane/srepkg_pkgs")

    srepkg_command = rep_int.SrepkgCommand(
        orig_pkg_ref=sample_pkgs.testproj,
        dist_out_dir=str(dist_out_dir),
        construction_dir=str(construction_dir))

    service_class_builder = sb.ServiceBuilder(srepkg_command)
    repackager = rep.Repackager(
        srepkg_command=srepkg_command,
        service_class_builder=service_class_builder)

    # with mock.patch.object(s_bldr.SrepkgBuilder, "build", return_value=None)\
    #         as mock_build:
    #     repackager.repackage()
    #     mock_build.assert_called_once_with()

    repackager.repackage()
