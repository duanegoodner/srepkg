from pathlib import Path
from typing import List
import srepkg.path_builders.file_structures as fs


def file_structure_walk(file_structure: List, root_path: Path,
                 shortcut_names=None, paths=None):
    if shortcut_names is None:
        shortcut_names = []
    if paths is None:
        paths = []

    for item in file_structure:
        shortcut_names.append(item.sc)
        paths.append(root_path / item.pname)
        if type(item) == fs.SCD:
            new_names, new_paths = file_structure_walk(
                file_structure=item.contents, root_path=root_path / item.pname)
            shortcut_names += new_names
            paths += new_paths

    return shortcut_names, paths


def build_paths_class(shortcut_names: List[str], class_name: str,
                      write_path: Path):
    with write_path.open(mode='w') as class_file:
        class_file.write('from typing import NamedTuple\n'
                         'from pathlib import Path\n\n\n'
                         f'class {class_name}(NamedTuple):\n')
        for name in shortcut_names:
            class_file.write(f'    {name}: Path\n')


def main():
    src_names, src_paths = file_structure_walk(
        fs.install_components, Path(__file__).parent.parent.absolute() /
        'install_components')

    builder_src_paths_path = Path(__file__).parent.absolute() / \
        'builder_src_paths.py'
    build_paths_class(src_names, 'BuilderSrcPaths', builder_src_paths_path)

    dest_names, dest_paths = file_structure_walk(fs.get_builder_dest(),
                                          Path('srepkg_pkgs'))
    builder_dest_paths_path = Path(__file__).parent.absolute() / \
        'builder_dest_paths.py'
    build_paths_class(dest_names, 'BuilderDestPaths', builder_dest_paths_path)


if __name__ == '__main__':
    main()
