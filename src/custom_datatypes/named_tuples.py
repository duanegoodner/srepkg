from pathlib import Path
from typing import NamedTuple, List

# TODO divide up into more specific modules


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


SCF = NamedTuple('SCF', [('pname', str), ('sc', str)])
SCD = NamedTuple('SCD', [('pname', str), ('sc', str), ('contents', List)])

