import pytest
from dataclasses import dataclass
from pathlib import Path
import srepkg.repackager_data_structs as rep_ds
from srepkg.construction_dir import TempConstructionDir
import srepkg.logging_initializer as lgr


@dataclass
class AllExamplePackages:
    src_dir = Path(__file__).parent.absolute() / "package_test_cases"
    tproj_non_pure_py: str = str(src_dir / "mock_non_pure_python_pkg")
    testproj: str = str(src_dir / "testproj")
    testprojhypenentry: str = str(src_dir / "testprojhypenentry")
    testprojhyphenentry_whl: str = str(
        src_dir / "testprojhyphenentry-0.0.0-py3-none-any.whl"
    )
    testprojnoentry_whl: str = str(
        src_dir / "testprojnoentry-0.0.0-py3-none-any.whl"
    )
    testprojnoconsolescript_section_whl: str = str(
        src_dir / "testprojnoconsolescripts-0.0.0-py3-none-any.whl"
    )
    testproj_whl: str = str(src_dir / "testproj-0.0.0-py3-none-any.whl")
    testproj_targz: str = str(src_dir / "testproj-0.0.0.tar.gz")
    testproj_zip: str = str(src_dir / "testproj-0.0.0.zip")
    numpy_whl: str = str(
        src_dir / "numpy-1.23.2-cp39-cp39-macosx_10_9_x86_64.whl"
    )
    black_py_pi: str = "black"
    black_22p1p0_macosx_whl: str = str(
        src_dir / "black-22.1.0-cp310-cp310-macosx_10_9_x86_64.whl"
    )
    scrape_py_pi: str = "scrape"
    numpy_py_pi: str = "numpy"
    howdoi_github: str = "https://github.com/gleitz/howdoi"
    black_github: str = "https://github.com/psf/black"
    wheel_inspect_whl: str = str(
        src_dir / "wheel_inspect-1.7.1-py3-none-any.whl"
    )
    wheel_missing_dist_info: str = str(
        src_dir / "packagemissingdistinfo-0.1-py3-none-any.whl"
    )
    wheel_multi_dist_info: str = str(
        src_dir / "packagemultidistinfo-0.1-py3-none-any.whl"
    )
    cowsay_py_pi: str = "cowsay"
    innder_pkg_testproj_setup_cfg: str = str(
        src_dir / "inner_pkg_testproj_setup.cfg"
    )


@pytest.fixture
def sample_pkgs():
    return AllExamplePackages()


@pytest.fixture
def tmp_construction_dir():
    return TempConstructionDir()


@pytest.fixture
def dummy_cdir_args():
    return {
        "pkg_name": "dummy",
        "pkg_version": "dummy",
        "srepkg_name": "dummy",
        "srepkg_root": Path("dummy"),
        "orig_pkg_dists": Path("dummy"),
        "srepkg_inner": Path("dummy"),
    }


@pytest.fixture
def dummy_cdir_summary():
    return rep_ds.ConstructionDirSummary(
        pkg_name="dummy",
        pkg_version="dummy",
        srepkg_name="dummy",
        srepkg_root=Path("dummy"),
        orig_pkg_dists=Path("dummy"),
        srepkg_inner=Path("dummy"),
    )


@pytest.fixture
def app_logger():
    app_logger = lgr.LoggingInitializer()
    app_logger.setup()
    return app_logger
