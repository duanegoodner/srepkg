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
    inner_pkg: Path
    main_inner: Path
    main_inner_orig: Path
    pkg_names_inner: Path
    srepkg_init: Path
    main_outer: Path
    pkg_names_mid: Path
    inner_setup_cfg_active: Path
    inner_setup_cfg_inactive: Path
    inner_setup_py_active: Path
    inner_setup_py_inactive: Path
    inner_pkg_installer: Path
    manifest: Path
    pkg_names_outer: Path
    srepkg_setup_cfg: Path
    srepkg_setup_py: Path
