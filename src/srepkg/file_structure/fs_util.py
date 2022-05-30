from pathlib import Path
from typing import List
from custom_datatypes.named_tuples import SCD


def _file_structure_walk(file_structure: List, root_path: Path,
                        shortcut_names=None, paths=None):
    if shortcut_names is None:
        shortcut_names = []
    if paths is None:
        paths = []

    for item in file_structure:
        shortcut_names.append(item.sc)
        paths.append(root_path / item.pname)
        if type(item) == SCD:
            new_names, new_paths = _file_structure_walk(
                file_structure=item.contents, root_path=root_path / item.pname)
            shortcut_names += new_names
            paths += new_paths

    return shortcut_names, paths


class FileStructureUtil:
    def __init__(self, file_struct: List, root_path: Path):
        self._file_struct = file_struct
        self._root_path = root_path

    def get_sc_and_path_names(self):
        return _file_structure_walk(self._file_struct, self._root_path)

    def get_sc_names(self):
        return self.get_sc_and_path_names()[0]

    def get_path_names(self) -> List:
        return self.get_sc_and_path_names()[1]

    def build_paths_class(self, class_name: str, write_file_path: Path):
        shortcut_names = self.get_sc_names()
        with write_file_path.open(mode='w') as class_file:
            class_file.write('from typing import NamedTuple\n'
                             'from pathlib import Path\n\n\n'
                             f'class {class_name}(NamedTuple):\n')
            for name in shortcut_names:
                class_file.write(f'    {name}: Path\n')


# def create_builder_paths_class_files():
#     src_files_util = FileStructureUtil(
#         file_struct=fs.repackaging_components,
#         root_path=Path(__file__).parent.parent.absolute() /
#         'repackaging_components')
#     builder_src_class_file = Path(__file__).parent.parent.parent.absolute() / \
#         'custom_datatypes' / 'builder_src_paths.py'
#     src_files_util.build_paths_class(class_name='BuilderSrcPaths',
#                                      write_file_path=builder_src_class_file)
#
#     dest_files_util = FileStructureUtil(
#         file_struct=fs.get_builder_dest(), root_path=Path('srepkg_pkgs')
#     )
#     builder_dest_class_file = Path(__file__).parent.parent.parent.absolute() / \
#         'custom_datatypes' / 'builder_dest_paths.py'
#     dest_files_util.build_paths_class(class_name='BuilderDestPaths',
#                                       write_file_path=builder_dest_class_file)
#
#
# if __name__ == '__main__':
#     create_builder_paths_class_files()