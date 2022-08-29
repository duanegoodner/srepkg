import pytest
import srepkg.dist_provider as d_prov
from pathlib import Path
from srepkg.test.shared_fixtures import sample_pkgs, tmp_construction_dir


class TestDistProvider:

    @pytest.mark.parametrize("provider_constructor, src_path, num_orig_pkgs", [
        (d_prov.DistProviderFromSrc, "testproj", 1),
        (d_prov.DistProviderFromSrc, "tproj_non_pure_py", 2),
        (d_prov.DistCopyProvider, "testproj_targz", 1)
    ])
    def test_provider_sources(self, provider_constructor, src_path,
                              tmp_construction_dir, sample_pkgs, num_orig_pkgs):
        dist_provider = provider_constructor(
            src_path=Path(getattr(sample_pkgs, src_path)),
            dest_path=tmp_construction_dir.orig_pkg_dists)
        dist_provider.run()
        assert len(list(
            tmp_construction_dir.orig_pkg_dists.iterdir())) == num_orig_pkgs
