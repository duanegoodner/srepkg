from enum import Enum
from typing import NamedTuple


class ErrorMsg(NamedTuple):
    msg: str


class OrigPkgError(ErrorMsg, Enum):
    PkgPathNotFound = ErrorMsg(msg="Original package path not found")
    SetupPyNotFound = ErrorMsg(
        msg="No setup.py file found. srepkg requires a setup.py file with call"
        "to setuptools.setup()"
    )
    NoCSE = ErrorMsg(msg="No console script entry points found")


class SetupFileReaderError(ErrorMsg, Enum):
    SetupCfgReadError = ErrorMsg(msg="Unable to read or parse setup.cfg")
    UnsupportedSetupFileType = ErrorMsg(msg="Unsupported setup file type")


class SrepkgBuilderError(ErrorMsg, Enum):
    OrigPkgPathNotFound = ErrorMsg(msg="Original package path not found")
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


class PkgRetrieverError(ErrorMsg, Enum):
    InvalidPkgRef = ErrorMsg(
        msg="Package reference provided to srepkg is not recognized as a valid "
        "package."
    )


class PkgIdentifierError(ErrorMsg, Enum):
    PkgNotFound = ErrorMsg(
        msg="Package reference provided to srepkg is not recognized as a valid "
        "package."
    )
    MultiplePotentialPackages = ErrorMsg(
        msg="Package reference is consistent with more than one package."
    )


class ConstructionDirError(ErrorMsg, Enum):
    MissingORigPkgContent = ErrorMsg(
        msg="Srepkg construction directory does not contain any original "
        "content. Expect to find a wheel or source distribution, but "
        "neither found."
    )
    MultiplePackagesPresent = ErrorMsg(
        msg="Srepkg build directory contains distributions from multiple "
        "packages and/or versions."
    )
    TargetDistTypeNotSupported = ErrorMsg(
        msg="Srepkg does not support conversion of original package to this "
        "type"
    )
    NoSDistForWheelConstruction = ErrorMsg(
        msg="Conversion of Sdist to Wheel is requested, but no Sdist found in "
        "srepkg construction directory."
    )


class EntryPontExtractorError(ErrorMsg, Enum):
    NoEntryPointsFile = ErrorMsg(
        msg="No entry_points.txt file found in wheel."
    )


class ArchiveFileError(ErrorMsg, Enum):
    UnsupportedFileType = ErrorMsg(
        msg="Extraction of item at provided path is not supported."
    )
