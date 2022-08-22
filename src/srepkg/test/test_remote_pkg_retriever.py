import pytest
import srepkg.remote_pkg_retriever as rpr
from srepkg.test.shared_fixtures import sample_pkgs, tmp_construction_dir


class TestRemotePackageRetriever:

    @pytest.mark.parametrize("pkg_retriever, t_pkg_ref", [
        ("NullPkgRetriever", "testproj",),
        ("NullPkgRetriever", "tproj_non_pure_py"),
        ("PyPIPkgRetriever", "scrape_py_pi"),
        ("GithubPkgRetriever", "howdoi_github")
    ])
    def test_retriever(self, pkg_retriever, t_pkg_ref, sample_pkgs, tmp_construction_dir):
        retriever_constructor = getattr(rpr, pkg_retriever)
        retriever_constructor(
            pkg_ref=getattr(sample_pkgs, t_pkg_ref),
            copy_dest=tmp_construction_dir).retrieve()

