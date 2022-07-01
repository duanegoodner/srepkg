import abc
import subprocess
import sys
import tempfile
import wheel_inspect as wi
from pathlib import Path
from shared_data_structures.named_tuples import OrigPkgInfo
from typing import Callable, NamedTuple

import shared_data_structures as sd
from utils.cd_context_manager import dir_change_to


class DistInfoFile(NamedTuple):
    filename: str
    parser: Callable
    save_as_key: str


class OrigPkgInspector(abc.ABC):

    @abc.abstractmethod
    def get_orig_pkg_info(self) -> OrigPkgInfo:
        pass


class SrcCodeInspector(OrigPkgInspector):
    DIST_INFO_FILES_OF_INTEREST = [
        DistInfoFile(filename='METADATA',
                     parser=wi.metadata.parse_metadata,
                     save_as_key='metadata'
                     ),
        DistInfoFile(filename='entry_points.txt',
                     parser=wi.inspecting.parse_entry_points,
                     save_as_key='entry_points')
    ]

    def __init__(self, orig_pkg_path: Path):
        self._orig_pkg_path = orig_pkg_path

    def get_dist_info(self) -> dict[str, dict]:

        dist_info = {}

        dist_info_root = tempfile.TemporaryDirectory()
        # dist_info_dir = Path('/Users/duane/dproj/srepkg/src/srepkg/test')

        with dir_change_to(self._orig_pkg_path):
            subprocess.call([sys.executable, 'setup.py', 'dist_info', '-e',
                             dist_info_root.name])

        items_in_dist_info_dir = list(Path(str(dist_info_root.name)).iterdir())
        assert len(items_in_dist_info_dir) == 1
        dist_info_dir = items_in_dist_info_dir[0]

        for file in self.DIST_INFO_FILES_OF_INTEREST:
            if (Path(str(dist_info_dir)) / file.filename).exists():
                with (Path(str(dist_info_dir)) / file.filename).open(mode='r') \
                        as df:
                    dist_info[file.save_as_key] = file.parser(df)

        dist_info_root.cleanup()

        return dist_info

    def get_orig_pkg_info(self) -> OrigPkgInfo:
        dist_info = self.get_dist_info()
        return OrigPkgInfo(
            pkg_name=dist_info['metadata']['name'],
            version=dist_info['metadata']['version'],
            root_path=self._orig_pkg_path,
            entry_pts=sd.console_script_entry.CSEntryPoints.
            from_wheel_inspect_cs(
                dist_info['entry_points']['console_scripts']).as_cse_obj_list
        )
