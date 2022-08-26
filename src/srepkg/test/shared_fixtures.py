import pytest
from dataclasses import dataclass
from pathlib import Path
from srepkg.construction_dir import TempConstructionDir


@dataclass
class AllExamplePackages:
    src_dir = Path(__file__).parent.absolute() / 'package_test_cases'
    tproj_non_pure_py: str = str(src_dir / "mock_non_pure_python_pkg")
    testproj: str = str(src_dir / "testproj")
    testproj_whl: str = str(src_dir / "testproj-0.0.0-py3-none-any.whl")
    testproj_targz: str = str(src_dir / "testproj-0.0.0.tar.gz")
    testproj_zip: str = str(src_dir / "testproj-0.0.0.zip")
    numpy_whl: str = str(
        src_dir / "numpy-1.23.2-cp39-cp39-macosx_10_9_x86_64.whl")
    black_py_pi: str = "black"
    scrape_py_pi: str = "scrape"
    numpy_py_pi: str = "numpy"
    howdoi_github: str = "https://github.com/gleitz/howdoi.git"
    black_github: str = "https://github.com/psf/black"
    wheel_inspect_whl: str = str(src_dir / "wheel_inspect-1.7.1-py3-none-any.whl")


@pytest.fixture
def sample_pkgs():
    return AllExamplePackages()


@pytest.fixture
def tmp_construction_dir():
    return TempConstructionDir()


