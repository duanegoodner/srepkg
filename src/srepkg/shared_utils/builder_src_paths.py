from typing import NamedTuple
from pathlib import Path


class BuilderSrcPaths(NamedTuple):
    srepkg_control_components: Path
    srepkg_control_components_init: Path
    entry_module: Path
    srepkg_control_paths: Path
    srepkg_controller: Path
    template_files: Path
    manifest_template: Path
    pkg_names_template: Path
    repackaging_components_init: Path
    entry_point_template: Path
    inner_pkg_installer: Path
    main_inner: Path
    main_outer: Path
    srepkg_setup_py: Path
    srepkg_setup_cfg: Path
    srepkg_init: Path
