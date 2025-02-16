import pytest
import srepkg.error_handling.custom_exceptions as ce
import srepkg.repackager_interfaces as rep_int
import srepkg.service_builder as sb
from test.shared_fixtures import sample_pkgs
import srepkg.utils.dist_archive_file_tools as daft


class TestOrigSrcPreparer:

    @pytest.mark.parametrize(
        "pkg_ref, git_ref, version_command, expected_archive_types",
        [
            ("testproj", None, None, {daft.ArchiveDistType.WHEEL}),
            ("testproj_whl", None, None, {daft.ArchiveDistType.WHEEL}),
            (
                "testproj_targz",
                None,
                None,
                {daft.ArchiveDistType.SDIST, daft.ArchiveDistType.WHEEL},
            ),
            (
                "testproj_zip",
                None,
                None,
                {daft.ArchiveDistType.SDIST, daft.ArchiveDistType.WHEEL},
            ),
            # ("black_github", None, None, {daft.ArchiveDistType.WHEEL}),
            (
                "black_github",
                "767604e03f5e454ae5b5c268cd5831c672f46de8",
                None,
                {daft.ArchiveDistType.WHEEL},
            ),
            ("scrape_py_pi", None, "0.11.1", {daft.ArchiveDistType.WHEEL}),
        ],
    )
    def test_sources(
        self,
        pkg_ref,
        git_ref,
        version_command,
        expected_archive_types,
        sample_pkgs,
    ):
        cmd = rep_int.SrepkgCommand(
            orig_pkg_ref=getattr(sample_pkgs, pkg_ref),
            git_ref=git_ref,
            pypi_version=version_command,
        )
        src_preparer = sb.ServiceBuilder(cmd).create_orig_src_preparer()
        src_preparer.prepare()
        final_dist_types = {
            daft.ArchiveIdentifier().id_dist_type(item)
            for item in src_preparer._receiver._orig_pkg_dists_contents
        }
        assert expected_archive_types == final_dist_types

    def test_bad_commit_ref(self, sample_pkgs):
        cmd = rep_int.SrepkgCommand(
            orig_pkg_ref=sample_pkgs.black_github, git_ref="bad_commit_ref"
        )
        src_preparer = sb.ServiceBuilder(cmd).create_orig_src_preparer()
        with pytest.raises(ce.GitCheckoutError):
            src_preparer.prepare()
