from pathlib import Path
from typing import List
from srepkg.shared_data_structures.named_tuples import SCD


def _file_structure_walk(
    file_structure: List, root_path: Path, shortcut_names=None, paths=None
):
    if shortcut_names is None:
        shortcut_names = []
    if paths is None:
        paths = []

    for item in file_structure:
        shortcut_names.append(item.sc)
        paths.append(root_path / item.pname)
        if type(item) == SCD:
            new_names, new_paths = _file_structure_walk(
                file_structure=item.contents, root_path=root_path / item.pname
            )
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
