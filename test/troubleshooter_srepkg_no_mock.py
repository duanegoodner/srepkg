import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))    

from shared_fixtures import sample_pkgs

import srepkg.repackager as rep
from srepkg.srepkg import main


def test_srepkg(mocker, sample_pkgs):
    # mocker.patch.object(rep.Repackager, "repackage", return_value=None)

    # main([sample_pkgs.oldmath, "-d", "/Users/duane/srepkg_pkgs", "-n"
    #       "from_script"])

    main(["black", "-r", "23.1.0"])


def run_repkg():
    main(["black", "-r", "23.1.0"])


if __name__ == "__main__": 
    run_repkg()
