import srepkg.dist_builder_sub_process as dbs
import tempfile
from test.shared_fixtures import sample_pkgs


def test_dist_builder_subprocess(sample_pkgs):
    construction_dir = tempfile.TemporaryDirectory()
    args = ("wheel", sample_pkgs.testproj, construction_dir.name)
    dist_path = dbs.main(args)
    assert dist_path.exists()
    assert dist_path.name.endswith(".whl")


