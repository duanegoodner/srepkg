import entry_points_txt
import pytest
from pathlib import Path
from zipfile import ZipFile
import srepkg.error_handling.custom_exceptions as ce
import srepkg.utils.wheel_entry_point_extractor as we_pe
from test.shared_fixtures import sample_pkgs


@pytest.fixture
def testproj_wheel(sample_pkgs):
    return we_pe.WheelEntryPointExtractor(Path(sample_pkgs.testproj_whl))


class TestWheelEntryPointExtractor:

    def test_no_entry_pts_text(self, mocker, testproj_wheel):
        mocker.patch.object(ZipFile, "namelist", return_value=[])
        with pytest.raises(ce.NoEntryPtsTxtFile):
            testproj_wheel.get_entry_points()

    def test_multiple_entry_pts_text(self, mocker, testproj_wheel):
        mocker.patch.object(
            ZipFile,
            "namelist",
            return_value=["dir1/entry_points.txt", "dir2/entry_points.txt"],
        )
        with pytest.raises(ce.MultipleEntryPtsTxtFiles):
            testproj_wheel.get_entry_points()

    def test_no_console_scripts(self, mocker, testproj_wheel):
        mocker.patch.object(
            entry_points_txt, "load", return_value={"console_scripts": {}}
        )
        with pytest.raises(ce.NoConsoleScriptEntryPoints):
            testproj_wheel.get_entry_points()
