from .error_messages import SetupFileReaderError
from .error_messages import PkgRetrieverError


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


# class LocalPathNotRecognizedAsPackage(Exception):
#     def __init__(
#             self,
#             path_name: str,
#             msg=PkgRetrieverError.NotRecognizedAsPackage.msg):
#         self._path_name = path_name
#         self._msg = msg
#
#     def __str__(self):
#         return f"{self._path_name} -> {self._msg}"


class InvalidPkgRef(Exception):
    def __init__(
            self,
            pkg_ref: str,
            msg=PkgRetrieverError.InvalidPkgRef.msg):
        self._pkg_ref = pkg_ref
        self._msg = msg

    def __str__(self):
        return f"{self._pkg_ref} -> {self._msg}"
