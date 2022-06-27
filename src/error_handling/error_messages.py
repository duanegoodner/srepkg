from enum import Enum
from typing import NamedTuple


class ErrorMsg(NamedTuple):
    msg: str


class OrigPkgError(ErrorMsg, Enum):
    PkgPathNotFound = ErrorMsg(msg="Original package path not found")
    NoSetupFilesFound = ErrorMsg(
        msg="No setup.py file found, and no setup.cfg file found.\nsrepkg "
        "needs at least one of these files."
    )
    PkgNameNotFound = ErrorMsg(
        msg="Unable to find package name in any setup file"
    )
    InvalidPkgName = ErrorMsg(msg="Invalid package name")
    SetupCfgReadError = ErrorMsg(msg="Unable to read or parse setup.cfg")
    NoCSE = ErrorMsg(msg="No console script entry points found")


class SetupFileReaderError(ErrorMsg, Enum):
    SetupCfgReadError = ErrorMsg(msg="Unable to read or parse setup.cfg")
    UnsupportedSetupFileType = ErrorMsg(msg="Unsupported setup file type")


class SrepkgBuilderError(ErrorMsg, Enum):
    OrigPkgPathNotFound = ErrorMsg(
        msg="Original package path not found"
    )
    DestPkgPathExits = ErrorMsg(
        msg="Intended Srepkg destination path already exists"
    )
    ControlComponentsNotFound = ErrorMsg(
        msg="Error when attempting to copy sub-package "
            "srepkg_control_components. Sub-package not found"
    )
    ControlComponentsExist = ErrorMsg(
        msg="Error when attempting to copy sub-package "
            "srepkg_control_components. Destination path already exists."
    )
    FileNotFoundForCopy = ErrorMsg(
        msg="Error when attempting to copy. Source file not found."
    )
    CopyDestinationPathExists = ErrorMsg(
        msg="Error when attempting to copy. Destination path already exists"
    )