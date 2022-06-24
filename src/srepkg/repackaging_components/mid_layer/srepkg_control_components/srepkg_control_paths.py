from sys import version_info
from typing import NamedTuple
from pathlib import Path


class VenvPaths(NamedTuple):
    site_pkgs: Path
    vbin: Path
    py_interp: Path
    pip_exe: Path

    @classmethod
    def default(cls, venv_root: Path):

        py_version = (
            "python" + str(version_info.major) + "." + str(version_info.minor)
        )

        vbin = venv_root / "bin"

        return cls(
            site_pkgs=venv_root / "lib" / py_version / "site-packages",
            vbin=vbin,
            py_interp=vbin / "python",
            pip_exe=vbin / "pip",
        )
