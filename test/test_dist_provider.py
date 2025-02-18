import pytest
import srepkg.dist_provider as d_prov
import tempfile
from pathlib import Path
from test.shared_fixtures import sample_pkgs, tmp_construction_dir


class TestDistProvider:

    @pytest.mark.parametrize(
        "provider_constructor, commit_ref, src_path, num_orig_pkgs",
        [
            (d_prov.DistProviderFromSrc, None, "testproj", 1),
            (d_prov.DistProviderFromSrc, None, "tproj_non_pure_py", 2),
            (d_prov.DistCopyProvider, None, "testproj_targz", 1),
        ],
    )
    def test_provider_sources(
        self,
        provider_constructor,
        commit_ref,
        src_path,
        tmp_construction_dir,
        sample_pkgs,
        num_orig_pkgs,
    ):
        constructor_args = {
            "src_path": Path(getattr(sample_pkgs, src_path)),
            "dest_path": tmp_construction_dir.orig_pkg_dists,
        }

        dist_provider = provider_constructor(**constructor_args)
        dist_provider.run()
        assert (
            len(list(tmp_construction_dir.orig_pkg_dists.iterdir()))
            == num_orig_pkgs
        )

    def test_null_github_repo(self):
        src_path = Path(tempfile.TemporaryDirectory().name)
        dest_path = Path(tempfile.TemporaryDirectory().name)
        null_git_dist_provider = d_prov.DistProviderFromGitRepo(src_path, dest_path)
        null_git_dist_provider.checkout_commit_ref()
