import inspect
from pathlib import Path
from typing import List
import srepkg.file_structure as fs


class PathsClassBuilder:

    def __init__(self, file_struct: List, root_path: Path, class_name: str,
                 write_file_path: Path):
        self._file_struct_util = fs.fs_util.FileStructureUtil(
            file_struct, root_path)
        self._class_name = class_name
        self._write_file_path = write_file_path

    def write_class_file(self):
        shortcut_names = self._file_struct_util.get_sc_names()
        with self._write_file_path.open(mode='w') as class_file:
            class_file.write('from typing import NamedTuple\n'
                             'from pathlib import Path\n\n\n'
                             f'class {self._class_name}(NamedTuple):\n')
            for name in shortcut_names:
                class_file.write(f'    {name}: Path\n')


def build_for_srepkg():
    cd_path = Path(__file__).parent.parent.absolute() / 'custom_datatypes'

    PathsClassBuilder(
        file_struct=fs.fs_specs.repackaging_components,
        root_path=Path(inspect.getfile(fs)).parent.parent.absolute() /
        'repackaging_components',
        class_name='BuilderSrcPaths',
        write_file_path=cd_path / 'builder_src_paths.py')\
        .write_class_file()

    PathsClassBuilder(
        file_struct=fs.fs_specs.get_builder_dest(),
        root_path=Path('srepkg_pkgs'),
        class_name='BuilderDestPaths',
        write_file_path=cd_path / 'builder_dest_paths.py') \
        .write_class_file()


if __name__ == '__main__':
    build_for_srepkg()
