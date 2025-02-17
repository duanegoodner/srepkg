import srepkg.dist_builder_sub_process as dbs
import tempfile
import shared_fixtures as sf


if __name__ == "__main__":
    
    source_dir = sf.AllExamplePackages().testproj
    output_dir = tempfile.TemporaryDirectory()

    args = ("wheel", source_dir, output_dir.name)

    dbs.main(args)

