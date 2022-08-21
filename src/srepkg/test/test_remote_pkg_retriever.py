from pathlib import Path
import srepkg.construction_dir as cdn
import srepkg.remote_pkg_retriever as rpr


class TestRemotePackageRetriever:

    local_test_pkgs_path = Path(__file__).parent.absolute() / \
                           "package_test_cases"

    def setup_method(self):
        self.construction_dir = cdn.TempConstructionDir()

    def test_null_pkg_retriever(self):
        null_pkg_retriever = rpr.NullPkgRetriever(
            pkg_ref=str(self.local_test_pkgs_path / "testproj"),
            copy_dest=self.construction_dir)

        null_pkg_retriever.retrieve()

    def test_pypi_pkg_retriever(self):
        pypi_pkg_retriever = rpr.PyPIPkgRetriever(
            pkg_ref="scrape",
            copy_dest=self.construction_dir)
        pypi_pkg_retriever.retrieve()

    def test_github_pkg_retriever(self):
        github_pkg_retriever = rpr.GithubPkgRetriever(
            pkg_ref="https://github.com/gleitz/howdoi.git",
            copy_dest=self.construction_dir)
        github_pkg_retriever.retrieve()

