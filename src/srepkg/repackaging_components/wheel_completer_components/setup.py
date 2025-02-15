"""
Used building a wheel distribution of re-packaged package.
"""

import setuptools
import zipfile
from pathlib import Path


class LocalOrigWheelExaminer:
    """
    Determines whether the original package wheel is pure python or
    platform-specific
    """
    def __init__(self):
        """
        Initializes the path of directory containing original package
        wheel. Location relative to Path(__file__) is known based on
        file structure design spec.
        """
        self.orig_dist_dir = Path(__file__).parent / "orig_dist"

    @property
    def orig_wheel_path(self) -> Path:
        """
        Absolute path of the original package wheel.
        """
        orig_dist_dir = Path(__file__).parent / "orig_dist"
        orig_dist_wheels = [
            path
            for path in orig_dist_dir.iterdir()
            if path.name.endswith(".whl")
        ]
        if len(orig_dist_wheels) == 0:
            raise FileNotFoundError("Original package wheel not found.")
        if len(orig_dist_wheels) > 1:
            raise FileExistsError(
                "More than one original package wheel found."
            )
        return orig_dist_wheels[0]

    @property
    def wheel_contents(self) -> list[str]:
        """
        List of paths of all contents in wheel, relative to wheel root.
        """
        with zipfile.ZipFile(str(self.orig_wheel_path), mode="r") as whl:
            contents = whl.namelist()
        return contents

    @property
    def dist_info_dir(self) -> str:
        """
        Path of wheel's .dist-info directory, relative to wheel root.
        """
        dist_info_dirs = {
            path.split("/", 1)[0]
            for path in self.wheel_contents
            if path.split("/", 1)[0].endswith(".dist-info")
        }

        if len(dist_info_dirs) == 0:
            raise ValueError("No dist-info directory")
        if len(dist_info_dirs) > 1:
            raise ValueError("Multiple dist-info directories found")
        return next(iter(dist_info_dirs))

    @property
    def wheel_info_path(self) -> str:
        """
        Path of the WHEEL metadata file relative to wheel root.
        """
        return f"{self.dist_info_dir}/WHEEL"

    @property
    def contains_wheel_info_file(self) -> bool:
        return self.wheel_info_path in self.wheel_contents

    @property
    def is_pure_python(self) -> bool | None:
        with zipfile.ZipFile(self.orig_wheel_path, mode="r") as whl:
            with whl.open(self.wheel_info_path) as f:
                for line in f.read().decode("utf-8").splitlines():
                    if line.startswith("Root-Is-Purelib:"):
                        return line.split(": ")[1].strip().lower() == "true"
        raise ValueError("Cannot determine if original package wheel is pure python")


class BinaryDistribution(setuptools.dist.Distribution):
    """Distribution which always forces a binary package with platform name"""

    def has_ext_modules(self):
        return True

orig_wheel_examiner = LocalOrigWheelExaminer()

if orig_wheel_examiner.is_pure_python:
    setuptools.setup()
else:
    setuptools.setup(distclass=BinaryDistribution)
