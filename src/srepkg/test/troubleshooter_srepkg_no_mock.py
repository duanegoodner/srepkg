from pathlib import Path
import srepkg.repackager as rep
from srepkg.srepkg import main
from srepkg.test.shared_fixtures import sample_pkgs


def test_srepkg(mocker, sample_pkgs):
    # mocker.patch.object(rep.Repackager, "repackage", return_value=None)

    # main([sample_pkgs.testproj, "-d", "/Users/duane/srepkg_pkgs", "-n"
    #       "from_script"])

    main([sample_pkgs.numpy_py_pi])
