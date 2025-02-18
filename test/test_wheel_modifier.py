import shutil

import pytest

import srepkg.wheel_modifier as wm
import tempfile
from pathlib import Path
from test.shared_fixtures import sample_pkgs, tmp_construction_dir


def wheel_modifier_helper(orig_wheel: str):
    # orig_wheel = sample_pkgs.testproj_whl
    build_dir = tempfile.TemporaryDirectory()
    shutil.copy(orig_wheel, build_dir.name)
    wheel_name = Path(orig_wheel).name

    temp_wheel_path = Path(build_dir.name) / wheel_name

    wheel_modifier = wm.WheelEntryPointsModifier(wheel_path=temp_wheel_path)
    wheel_modifier.modify_and_rebuild()


def test_wheel_modifier(sample_pkgs):
    wheel_modifier_helper(sample_pkgs.testproj_whl)


def test_missing_dist_info(sample_pkgs):
    with pytest.raises(FileNotFoundError):
        wheel_modifier_helper(sample_pkgs.wheel_missing_dist_info)

def test_multiple_dist_info(sample_pkgs):
    with pytest.raises(FileExistsError):
        wheel_modifier_helper(sample_pkgs.wheel_multi_dist_info)

def test_hyphenated_entry_point(sample_pkgs):
    wheel_modifier_helper(sample_pkgs.testprojhyphenentry_whl)

def test_wheel_dist_info_getters(sample_pkgs):
    wheel_dist_info = wm.WheelDistInfo(wheel_path=sample_pkgs.testproj_whl)
    has_entry_points_txt = wheel_dist_info.has_entry_points_txt
    assert has_entry_points_txt
    entry_points_txt_rel_path  = wheel_dist_info.entry_points_txt_rel_path
    assert entry_points_txt_rel_path is not None
    entry_points_config = wheel_dist_info.get_entry_points_config()
    assert entry_points_config is not None

def test_wheel_no_entry_points(sample_pkgs):
    wheel_dist_info = wm.WheelDistInfo(wheel_path=sample_pkgs.testprojnoentry_whl)
    assert not wheel_dist_info.has_entry_points_txt
    assert wheel_dist_info.entry_points_txt_rel_path is None
    assert wheel_dist_info.get_entry_points_config() is None
    assert len(wheel_dist_info.console_script_names) == 0

def test_wheel_with_entry_but_no_console_scripts(sample_pkgs):
    wheel_dist_info = wm.WheelDistInfo(wheel_path=sample_pkgs.testprojnoconsolescript_section_whl)
    assert len(wheel_dist_info.console_script_names) == 0
