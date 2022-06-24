"""
Uses args namespace from command_input module to calculate and validate source
and destination paths used when building a new sre-package from an existing
package.
"""

import sys
from pathlib import Path
import custom_datatypes.builder_dest_paths as bdp
import custom_datatypes.builder_src_paths as bsp
import custom_datatypes.named_tuples as nt
import srepkg.file_structure as pb


class BuilderPathsCalculator:
    # TODO validator method to confirm cur file structure matches paths classes

    # standard repackaging components location
    _repackaging_components = (
        Path(__file__).parent.absolute() / "repackaging_components"
    )

    # srepkg name suffix when default naming is used
    _auto_srepkg_suffix = "srepkg"

    def __init__(
        self,
        orig_pkg_info: nt.OrigPkgInfo,
        construction_dir: Path,
        srepkg_custom_name: str = None,
    ):

        self._orig_pkg_info = orig_pkg_info
        self._srepkg_custom_name = srepkg_custom_name
        self._construction_dir = construction_dir

    @property
    def _srepkg_name(self):
        if self._srepkg_custom_name:
            return self._srepkg_custom_name
        else:
            return self._orig_pkg_info.pkg_name + self._auto_srepkg_suffix

    @property
    def _srepkg_root(self):
        return self._construction_dir / (
            self._orig_pkg_info.pkg_name + "_as_" + self._srepkg_name
        )

    def _validate_srepkg_root(self):

        if self._srepkg_root.exists():
            err_msg = (
                f"Destination path {str(self._srepkg_root)} " f"already exists"
            )
            sys.exit(err_msg)

    def calc_src_paths(self):
        src_files_util = pb.fs_util.FileStructureUtil(
            file_struct=pb.fs_specs.repackaging_components,
            root_path=self._repackaging_components,
        )
        src_paths = src_files_util.get_path_names()

        return bsp.BuilderSrcPaths(*src_paths)

    def calc_dest_paths(self):
        dest_files_util = pb.fs_util.FileStructureUtil(
            file_struct=pb.fs_specs.get_srepkg_root(self._srepkg_name),
            root_path=self._srepkg_root
        )

        dest_paths = dest_files_util.get_path_names()
        return bdp.BuilderDestPaths(*dest_paths)

    def calc_builder_paths(self):
        self._validate_srepkg_root()
        src_paths = self.calc_src_paths()
        dest_paths = self.calc_dest_paths()

        return src_paths, dest_paths
