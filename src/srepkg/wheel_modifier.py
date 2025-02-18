from __future__ import annotations

import configparser
import contextlib
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Callable

from wheel.cli.pack import pack
from wheel.cli.unpack import unpack


def silent_unpack(path: str, dest: str):
    """Unpack a .whl file silently."""
    with open(os.devnull, 'w') as devnull:
        with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
            unpack(path, dest)

def silent_pack(directory: str, dest_dir: str, build_number: str | None):
    """Pack a directory into a .whl file silently."""
    with open(os.devnull, 'w') as devnull:
        with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
            pack(directory, dest_dir, build_number)

class WheelDistInfo:
    def __init__(self, wheel_path: Path):
        self.wheel_path = wheel_path
        with zipfile.ZipFile(wheel_path) as zip_file:
            wheel_relative_paths = zip_file.namelist()
        self.dist_info_dirname = self.get_dist_info_dirname(
            wheel_relative_paths=wheel_relative_paths
        )
        self.child_paths = [
            item
            for item in wheel_relative_paths
            if item.startswith(self.dist_info_dirname)
        ]

    @staticmethod
    def get_dist_info_dirname(wheel_relative_paths: list[str]) -> str:
        dist_info_dirs = {
            path.split("/", 1)[0]
            for path in wheel_relative_paths
            if path.split("/", 1)[0].endswith(".dist-info")
        }

        if len(dist_info_dirs) == 0:
            raise FileNotFoundError("No dist-info directory")
        if len(dist_info_dirs) > 1:
            raise FileExistsError("Multiple dist-info directories found")

        return next(iter(dist_info_dirs))

    @property
    def has_entry_points_txt(self) -> bool:
        return f"{self.dist_info_dirname}/entry_points.txt" in self.child_paths

    @property
    def entry_points_txt_rel_path(self) -> Path | None:
        if self.has_entry_points_txt:
            return Path(self.dist_info_dirname) / "entry_points.txt"

    def get_entry_points_config(self) -> configparser.ConfigParser | None:
        if self.has_entry_points_txt:
            with zipfile.ZipFile(self.wheel_path) as zip_file:
                temp_dir = tempfile.TemporaryDirectory()
                zip_file.extract(
                    member=str(self.entry_points_txt_rel_path),
                    path=temp_dir.name,
                )

                config = configparser.ConfigParser()
                config.read(
                    f"{temp_dir.name}/{self.dist_info_dirname}/entry_points.txt"
                )
            return config

    @property
    def console_script_names(self) -> list[str]:
        if not self.has_entry_points_txt:
            return []
        entry_points_config = self.get_entry_points_config()
        if not entry_points_config.has_section("console_scripts"):
            return []
        else:
            return list(dict(entry_points_config["console_scripts"]).keys())

    @property
    def has_console_script_name_with_dash(self) -> bool:
        return any(["-" in item for item in self.console_script_names])


class WheelEntryPointsModifier:
    def __init__(self, wheel_path: Path):
        self.wheel_path = wheel_path
        self.wheel_dist_info = WheelDistInfo(wheel_path=wheel_path)

    @staticmethod
    def fix_console_script_names(
        entry_points_config: configparser.ConfigParser,
    ):
        for orig_script_name, func in entry_points_config[
            "console_scripts"
        ].items():
            if "-" in orig_script_name:
                new_name = orig_script_name.replace("-", "_")
                entry_points_config.remove_option(
                    "console_scripts", orig_script_name
                )
                entry_points_config.set("console_scripts", new_name, func)

    def modify_entry_points_txt(
        self,
        unpacked_wheel_path: Path,
        config_modifier: Callable[[configparser.ConfigParser], None],
    ):
        entry_points_txt_path = (
            unpacked_wheel_path
            / self.wheel_dist_info.dist_info_dirname
            / "entry_points.txt"
        )
        entry_points_config = configparser.ConfigParser()
        entry_points_config.read(entry_points_txt_path)
        config_modifier(entry_points_config)
        with entry_points_txt_path.open(mode="w") as entry_points_txt_file:
            entry_points_config.write(entry_points_txt_file)

    def modify_and_rebuild(self):


        # unpack wheel
        unpack_dir = tempfile.TemporaryDirectory()
        silent_unpack(path=str(self.wheel_dist_info.wheel_path), dest=unpack_dir.name)
        unpacked_wheel = list(Path(unpack_dir.name).iterdir())[0]

        # modify entry_points.txt in unpacked wheel
        self.modify_entry_points_txt(
            unpacked_wheel_path=unpacked_wheel,
            config_modifier=self.fix_console_script_names,
        )

        # repack wheel
        rebuild_dir = tempfile.TemporaryDirectory()
        silent_pack(
            directory=str(unpacked_wheel),
            dest_dir=str(rebuild_dir.name),
            build_number=None,
        )
        new_wheel_path = next(Path(rebuild_dir.name).glob("*.whl"), None)

        # For testing, easier not do this check just let shutil raise Except
        # if not new_wheel_path:
        #     raise FileNotFoundError("Failed to create new wheel file")

        # overwrite old wheel with new
        shutil.move(str(new_wheel_path), str(self.wheel_dist_info.wheel_path))

        # clean up
        shutil.rmtree(rebuild_dir.name)


# if __name__ == "__main__":
#
#     my_wheel_path = (
#         (Path(__file__)).parent.parent.parent
#         / "numpy-2.2.2-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"
#     )
#     my_wheel_dist_info = WheelDistInfo(wheel_path=my_wheel_path)
#     my_dist_entry_points_config = my_wheel_dist_info.get_entry_points_config()
#     my_console_script_names = my_wheel_dist_info.console_script_names
#     print(my_console_script_names)
#
#     wheel_modifier = WheelEntryPointsModifier(my_wheel_path)
#     wheel_modifier.modify_and_rebuild()
#     updated_console_script_names = my_wheel_dist_info.console_script_names
#     print(updated_console_script_names)
