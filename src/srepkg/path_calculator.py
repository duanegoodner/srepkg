"""
Uses args namespace from command_input module to calculate and validate source
and destination paths used when building a new sre-package from an existing
package.
"""
import sys
from pathlib import Path
import srepkg.shared_utils as su
import srepkg.path_builders as pb


class BuilderPathsCalculator:
    # TODO validator method to confirm cur file structure matches paths classes

    # class variables for standard repackaging components location
    _repackaging_components = Path(__file__).parent.absolute() \
                              / 'repackaging_components'

    # class variables to define default srepkg location and name
    srepkg_pkgs_dir = Path.home() / 'srepkg_pkgs'
    auto_srepkg_suffix = 'srepkg'

    def __init__(self,
                 orig_pkg_info: su.named_tuples.OrigPkgInfo,
                 srepkg_custom_name: str = None):

        self._orig_pkg_info = orig_pkg_info
        self._srepkg_custom_name = srepkg_custom_name

    def calc_src_paths(self):
        src_files_util = pb.class_builder.FileStructureUtil(
            file_struct=pb.file_structures.repackaging_components,
            root_path=self._repackaging_components)
        src_paths = src_files_util.get_path_names()

        # src_names, src_paths = pb.class_builder.file_structure_walk(
        #     file_structure=pb.file_structures.repackaging_components,
        #     root_path=self._repackaging_components)
        return su.named_tuples.BuilderSrcPaths(*src_paths)

    def get_sre_pkg_info(self):

        if self._srepkg_custom_name:
            srepkg_name = self._srepkg_custom_name
        else:
            srepkg_name = self._orig_pkg_info.pkg_name + self.auto_srepkg_suffix

        dest_root_path = self.srepkg_pkgs_dir / (self._orig_pkg_info.pkg_name +
                                                 '_as_' + srepkg_name)

        if dest_root_path.exists():
            err_msg = f'Destination path {str(dest_root_path)} already exists'
            sys.exit(err_msg)

        return su.named_tuples.SrePkgInfo(pkg_name=srepkg_name,
                                          root_path=dest_root_path)

    def calc_dest_paths(self):

        srepkg_info = self.get_sre_pkg_info()

        builder_dest_structure = pb.file_structures.get_builder_dest(
            root_name=srepkg_info.root_path.name,
            srepkg_name=srepkg_info.pkg_name,
            inner_pkg_name=self._orig_pkg_info.pkg_name)

        dest_file_util = pb.class_builder.FileStructureUtil(
            file_struct=builder_dest_structure,
            root_path=self.srepkg_pkgs_dir
        )

        dest_paths = dest_file_util.get_path_names()

        return su.named_tuples.BuilderDestPaths(*dest_paths)

    def calc_builder_paths(self):
        src_paths = self.calc_src_paths()
        dest_paths = self.calc_dest_paths()
        # inner_pkg_src = \
        #     dest_paths.srepkg / self._orig_pkg_info.package_dir_path. \
        #     relative_to(self._orig_pkg_info.root_path) / \
        #     self._orig_pkg_info.pkg_name

        return src_paths, dest_paths#, inner_pkg_src
