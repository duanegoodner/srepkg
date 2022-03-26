"""
Uses args namespace from command_input module to calculate and validate source
and destination paths used when building a new sre-package from an existing
package.
"""
from pathlib import Path

import srepkg.shared_utils as su
import srepkg.path_builders as pb


def calc_builder_src_paths():
    repackaging_components = Path(
        __file__).parent.absolute() / 'repackaging_components'
    src_names, src_paths = pb.paths_class_builder.file_structure_walk(
        file_structure=pb.file_structures.repackaging_components,
        root_path=repackaging_components)
    return su.named_tuples.BuilderSrcPaths(*src_paths)


class DestPathCalculator:
    # TODO implement 'check' to ensure file structure is same now as it was when paths classes were created
    # ===== start of class variables =====
    srepkg_pkgs_dir = Path.home() / 'srepkg_pkgs'
    auto_srepkg_suffix = 'srepkg'
    # ===== end of class variables =====

    def __init__(self, orig_pkg_info: su.named_tuples.OrigPkgInfo,
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

        return su.named_tuples.SrePkgInfo(pkg_name=srepkg_name,
                                            root_path=dest_root_path)

    def build_dest_paths(self):

        srepkg_info = self.get_sre_pkg_info()

        builder_dest_structure = pb.file_structures.get_builder_dest(
            root_name=srepkg_info.root_path.name,
            srepkg_name=srepkg_info.pkg_name,
            inner_pkg_name=self._orig_pkg_info.pkg_name
        )
        dest_names, dest_paths = pb.paths_class_builder.file_structure_walk(
            file_structure=builder_dest_structure,
            root_path=self.srepkg_pkgs_dir
        )

        return su.named_tuples.BuilderDestPaths(*dest_paths)
