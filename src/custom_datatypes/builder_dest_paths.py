from typing import NamedTuple
from pathlib import Path


class BuilderDestPaths(NamedTuple):
    srepkg: Path
    srepkg_entry_points: Path
    srepkg_entry_points_init: Path
    entry_module: Path
    srepkg_init: Path
    inner_pkg_install_cfg: Path
    inner_pkg_installer: Path
    manifest: Path
    srepkg_setup_cfg: Path
    srepkg_setup_py: Path
