from pathlib import Path

import srepkg.construction_dir as cdn
import srepkg.dist_provider as d_prov


class TestDistProvider:

    local_test_pkgs_path = Path(__file__).parent.absolute() / \
                           "package_test_cases"

    def setup_method(self):
        self.construction_dir = cdn.TempConstructionDir()

    def test_null_dist_provider(self):
        dist_provider = d_prov.NullDistProvider(
            orig_pkg_path=str(self.local_test_pkgs_path / "testproj"),
            pkg_receiver=self.construction_dir)
        dist_provider.provide()

    def test_dist_provider_from_src(self):
        dist_provider = d_prov.DistProviderFromSrc(
            orig_pkg_path=str(self.local_test_pkgs_path / "testproj"),
            pkg_receiver=self.construction_dir)
        dist_provider.provide()

    def test_dist_provider_from_non_pure_python_src(self):
        dist_provider = d_prov.DistProviderFromSrc(
            orig_pkg_path=str(
                self.local_test_pkgs_path / "mock_non_pure_python_pkg"),
            pkg_receiver=self.construction_dir)
        dist_provider.provide()


    def test_dist_copy_provider(self):
        dist_provider = d_prov.DistCopyProvider(
            orig_pkg_path=str(
                self.local_test_pkgs_path / "testproj-0.0.0.tar.gz"),
            pkg_receiver=self.construction_dir)
        dist_provider.provide()


