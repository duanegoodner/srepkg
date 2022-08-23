import pytest
import srepkg.repackager_interfaces as rep_int
import srepkg.service_builder as sb
from srepkg.test.shared_fixtures import sample_pkgs
import srepkg.utils.dist_archive_file_tools as daft


class TestOrigSrcPreparer2:

    @pytest.mark.parametrize("pkg_ref, expected_archive_types", [
        ("testproj", {daft.ArchiveDistType.WHEEL}),
        ("testproj_whl", {daft.ArchiveDistType.WHEEL}),
        ("testproj_targz", {
            daft.ArchiveDistType.SDIST, daft.ArchiveDistType.WHEEL}),
        ("testproj_zip", {
            daft.ArchiveDistType.SDIST, daft.ArchiveDistType.WHEEL})
    ])
    def test_sources(self, pkg_ref, expected_archive_types, sample_pkgs):
        cmd = rep_int.SrepkgCommand(
            orig_pkg_ref=getattr(sample_pkgs, pkg_ref))
        src_preparer = sb.ServiceBuilder(cmd).create_orig_src_preparer()
        src_preparer.prepare()
        final_dist_types = {
            daft.ArchiveIdentifier().id_dist_type(item) for item in
            src_preparer._receiver._orig_pkg_dists_contents}
        assert expected_archive_types == final_dist_types
