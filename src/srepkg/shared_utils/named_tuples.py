from pathlib import Path
from typing import NamedTuple, List
from srepkg.shared_utils.builder_dest_paths import BuilderDestPaths
from srepkg.shared_utils.builder_src_paths import BuilderSrcPaths


class CSEntry(NamedTuple):
    command: str
    module_path: str
    funct: str


class OrigPkgInfo(NamedTuple):
    pkg_name: str
    root_path: Path
    entry_pts: List[CSEntry]


class SrePkgInfo(NamedTuple):
    pkg_name: str
    root_path: Path


class ErrorMsg(NamedTuple):
    msg: str

