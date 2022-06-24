from typing import NamedTuple
from pathlib import Path


class BuilderSrcPaths(NamedTuple):
    mid_layer: Path
    srepkg_control_components: Path
    srepkg_control_components_init: Path
    entry_module: Path
    srepkg_control_paths: Path
    srepkg_controller: Path
    entry_point_template: Path
    srepkg_init: Path
    outer_layer: Path
    inner_pkg_installer: Path
    manifest_template: Path
    srepkg_setup_py: Path
    srepkg_setup_cfg: Path
    template_files: Path
    pkg_names_template: Path
