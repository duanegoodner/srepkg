from typing import NamedTuple
from pathlib import Path


class BuilderDestPaths(NamedTuple):
    root: Path
    srepkg: Path
    srepkg_control_components: Path
    srepkg_control_components_init: Path
    entry_module: Path
    srepkg_control_paths: Path
    srepkg_controller: Path
    srepkg_entry_points: Path
    srepkg_entry_points_init: Path
    srepkg_init: Path
    pkg_names_mid: Path
    inner_setup_cfg: Path
    inner_setup_py: Path
    inner_pkg_installer: Path
    manifest: Path
    pkg_names_outer: Path
    srepkg_setup_cfg: Path
    srepkg_setup_py: Path
