import srepkg.dist_builder_sub_process as dbs
import tempfile
import shared_fixtures as sf
from pathlib import Path


if __name__ == "__main__":
    
    source_dir = sf.AllExamplePackages().testproj
    output_dir = tempfile.TemporaryDirectory()

    args = ("wheel", source_dir, output_dir.name)

    dist_path = dbs.main(args)
    assert dist_path.exists()
    assert dist_path.name.endswith(".whl")

