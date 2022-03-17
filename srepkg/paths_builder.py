from pathlib import Path
from new_structure import SCD, SCF, my_file_structure
from typing import List
from collections import namedtuple


def get_sc_names(file_structure: List, root_path: Path, sc_names=None,
                 paths=None):
    if sc_names is None:
        sc_names = []
    if paths is None:
        paths = []

    for item in file_structure:
        sc_names.append(item.sc)
        paths.append(root_path / item.pname)
        if type(item) == SCD:
            new_names, new_paths = get_sc_names(
                file_structure=item.contents, root_path=root_path / item.pname)
            sc_names += new_names
            paths += new_paths

    return sc_names, paths


name_list, path_list = get_sc_names(my_file_structure, Path('/Users/duane/srepkg_pkgs'))

DestPaths = namedtuple('DestPaths', name_list)
dest_paths = DestPaths(*path_list)

for path in dest_paths._fields:
    print(path, getattr(dest_paths, path), getattr(dest_paths, path).exists())

