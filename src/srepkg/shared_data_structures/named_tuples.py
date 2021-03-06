from pathlib import Path
from typing import NamedTuple, List
from .builder_src_paths import BuilderSrcPaths
from .builder_dest_paths import BuilderDestPaths
from .console_script_entry import CSEntryPt


class OrigPkgInfo(NamedTuple):
    pkg_name: str
    version: str
    root_path: Path
    entry_pts: List[CSEntryPt]


class SrePkgInfo(NamedTuple):
    pkg_name: str
    root_path: Path


class ErrorMsg(NamedTuple):
    msg: str


class TaskBuilderInfo(NamedTuple):
    orig_pkg_info: OrigPkgInfo
    src_paths: BuilderSrcPaths
    repkg_paths: BuilderDestPaths
    dist_out_dir: Path


SCF = NamedTuple("SCF", [("pname", str), ("sc", str)])
SCD = NamedTuple("SCD", [("pname", str), ("sc", str), ("contents", List)])
