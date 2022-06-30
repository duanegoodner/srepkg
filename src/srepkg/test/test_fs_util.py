from pathlib import Path
import srepkg.file_structure as fs


def test_file_structure_walk_empty_names_paths():
    fs.fs_util._file_structure_walk(
        file_structure=fs.fs_specs.repackaging_components,
        root_path=Path('.'),
        shortcut_names=[],
        paths=[]
    )

