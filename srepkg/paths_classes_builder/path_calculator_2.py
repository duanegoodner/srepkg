"""
Uses args namespace from command_input module to calculate and validate source
and destination paths used when building a new sre-package from an existing
package.
"""
from pathlib import Path
from typing import NamedTuple, List
from srepkg.paths_classes_builder.builder_src_paths import BuilderSrcPaths
from srepkg.paths_classes_builder.builder_dest_paths import BuilderDestPaths
from srepkg.paths_classes_builder.paths_builder import get_sc_names
import srepkg.paths_classes_builder.file_structures as fs
import srepkg.ep_console_script as epcs


class OrigPkgInfo(NamedTuple):
    pkg_name: str
    root_path: Path
    entry_pts: List[epcs.CSEntry]


class SrePkgInfo(NamedTuple):
    pkg_name: str
    root_path: Path


class PathCalculator:
    # TODO implement 'check' to ensure file structure is same now as it was when paths classes were created
    # ===== start of class variables =====
    install_components = Path(__file__).parent.parent.absolute() / 'install_components'
    src_names, src_paths = get_sc_names(file_structure=fs.install_components,
                                        root_path=install_components)
    builder_src_paths = BuilderSrcPaths(*src_paths)

    srepkg_pkgs_dir = Path.home() / 'srepkg_pkgs'
    auto_srepkg_suffix = 'srnew'
    # ===== end of class variables =====

    def __init__(self, orig_pkg_info: OrigPkgInfo,
                 srepkg_custom_name: str = None):
        self._orig_pkg_info = orig_pkg_info
        self._srepkg_custom_name = srepkg_custom_name

    @property
    def srepkg_custom_name(self):
        return self._srepkg_custom_name

    def get_sre_pkg_info(self):

        if self.srepkg_custom_name:
            srepkg_name = self.srepkg_custom_name
        else:
            srepkg_name = self._orig_pkg_info.pkg_name + self.auto_srepkg_suffix

        dest_root_path = self.srepkg_pkgs_dir / (self._orig_pkg_info.pkg_name +
                                                 '_as_' + srepkg_name)

        if dest_root_path.exists():
            print(f'Destination path {str(dest_root_path)} already exists')
            exit(1)

        return SrePkgInfo(pkg_name=srepkg_name, root_path=dest_root_path)

    def build_dest_paths(self):
        # TODO refactor / clean up gathering of names and root path to pass to fs.get_builder_dest

        srepkg_info = self.get_sre_pkg_info()

        builder_dest_structure = fs.get_builder_dest(
            root_name=srepkg_info.root_path.name,
            srepkg_name=srepkg_info.pkg_name,
            inner_pkg_name=self._orig_pkg_info.pkg_name
        )
        dest_names, dest_paths = get_sc_names(
            file_structure=builder_dest_structure,
            root_path=self.srepkg_pkgs_dir
        )

        return BuilderDestPaths(*dest_paths)
