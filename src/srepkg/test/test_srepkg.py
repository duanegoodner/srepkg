from pathlib import Path
from srepkg.srepkg import main


def test_srepkg(tmp_path):
    main([
        str(Path(__file__).parent / "package_test_cases" /
            "wheel_inspect-1.7.1-py3-none-any.whl"),
        # "--dist_out_dir", "/Users/duane/srepkg_pkgs",
        # "--construction_dir", "/Users/duane/srepkg_pkgs"
    ])
