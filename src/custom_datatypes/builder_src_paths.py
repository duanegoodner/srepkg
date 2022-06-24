from typing import NamedTuple
from pathlib import Path


class BuilderSrcPaths(NamedTuple):
    mid_layer: Path
    entry_module: Path
    entry_point_template: Path
    srepkg_init: Path
    outer_layer: Path
    inner_pkg_installer: Path
    manifest_template: Path
    srepkg_setup_py: Path
    srepkg_setup_cfg: Path
