from typing import List

from .error_messages import SetupFileReaderError
from .error_messages import PkgRetrieverError
from .error_messages import ConstructionDirError
from .error_messages import ArchiveFileError


class UnsupportedSetupFileType(Exception):
    def __init__(
            self,
            file_name: str,
            msg=SetupFileReaderError.UnsupportedSetupFileType.msg,
    ):
        self._file_name = file_name
        self._msg = msg
        super().__init__(self._msg)

    def __str__(self):
        return f"{self._file_name} -> {self._msg}"


class InvalidPkgRef(Exception):
    def __init__(
            self,
            pkg_ref: str,
            msg=PkgRetrieverError.InvalidPkgRef.msg):
        self._pkg_ref = pkg_ref
        self._msg = msg

    def __str__(self):
        return f"{self._pkg_ref} -> {self._msg}"


class MissingOrigPkgContent(Exception):
    def __init__(
            self,
            srepkg_content_path: str,
            msg=ConstructionDirError.MissingORigPkgContent.msg):
        self._srepkg_content_path = srepkg_content_path
        self._msg = msg

    def __str__(self):
        return f"{self._srepkg_content_path} -> {self._msg}"


class UnsupportedCompressionType(Exception):
    def __init__(
            self,
            unsupported_file: str,
            msg=ArchiveFileError.UnsupportedFileType.msg ):
        self._unsupported_file = unsupported_file
        self._msg = msg

    def __str__(self):
        return f"{self._unsupported_file} -> {self._msg}"


class MultiplePackagesPresent(Exception):
    def __init__(
            self,
            dists_info: List,
            msg=ConstructionDirError.MultiplePackagesPresent.msg):
        self._dists_info = dists_info
        self._msg = msg

    def __str__(self):
        return f"{self._dists_info} -> {self._msg}"


class TargetDistTypeNotSupported(Exception):
    def __init__(
            self,
            unsupported_dist_type,
            msg=ConstructionDirError.TargetDistTypeNotSupported.msg):
        self._unsupported_dist_type = unsupported_dist_type
        self._msg = msg

    def __str__(self):
        return f"{self._unsupported_dist_type} -> {self._msg}"


class NoSupportedSrcDistTypes(Exception):
    def __init__(
            self,
            msg=ConstructionDirError.TargetDistTypeNotSupported.msg):
        self._msg = msg

    def __str__(self):
        return self._msg

