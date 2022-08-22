import pytest
from dataclasses import dataclass
from pathlib import Path
from srepkg.construction_dir import TempConstructionDir


@dataclass
class AllExamplePackages:
    src_dir = Path(__file__).parent.absolute() / 'package_test_cases'
    tproj_non_pure_py: Path = src_dir / "mock_non_pure_python_pkg"
    testproj: Path = src_dir / "testproj"
    testproj_whl: Path = src_dir / "testproj-0.0.0-py3-none-any.whl"
    numpy_whl: Path = src_dir / "numpy-1.23.2-cp39-cp39-macosx_10_9_x86_64.whl"
    scrape_py_pi: str = "scrape"
    howdoi_github: str = "https://github.com/gleitz/howdoi.git"


@pytest.fixture
def sample_pkgs():
    return AllExamplePackages()


@pytest.fixture
def tmp_construction_dir():
    return TempConstructionDir()
