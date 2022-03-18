from pathlib import Path
from srepkg.paths_classes_builder.file_structures import SCD, \
    get_builder_dest, install_components
from typing import List


def get_sc_names(file_structure: List, root_path: Path,
                 sc_names=None, paths=None):
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


def build_paths_class(sc_names: List[str], class_name: str, write_path: Path):
    with write_path.open(mode='w') as class_file:
        class_file.write('from typing import NamedTuple\n'
                         'from pathlib import Path\n\n\n'
                         f'class {class_name}(NamedTuple):\n')
        for name in sc_names:
            class_file.write(f'    {name}: Path\n')


src_names, src_paths = get_sc_names(install_components,
                                    Path(__file__).parent.parent.absolute() /
                                    'install_components')

builder_src_paths_path = Path(__file__).parent.absolute() /\
                         'builder_src_paths.py'
build_paths_class(src_names, 'BuilderSrcPaths', builder_src_paths_path)


dest_names, dest_paths = get_sc_names(get_builder_dest(), Path('srepkg_pkgs'))
builder_dest_paths_path = Path(__file__).parent.absolute() /\
                          'builder_dest_paths.py'
build_paths_class(dest_names, 'BuilderDestPaths', builder_dest_paths_path)


# class TestTuple(NamedTuple):
#     item_1: Path
#     item_2: Path
#     item_3: Path
#
#
# this_thing = TestTuple(*my_names)
# print(this_thing)

# print(SrcPaths)
# print(dir(SrcPaths))
# print(SrcPaths.__dict__)

# name_list, path_list = get_sc_names(my_file_structure, Path('/Users/duane/srepkg_pkgs'))
#
# DestPaths = namedtuple('DestPaths', name_list)
# dest_paths = DestPaths(*path_list)
#
# for path in dest_paths._fields:
#     print(path, getattr(dest_paths, path), getattr(dest_paths, path).exists())
