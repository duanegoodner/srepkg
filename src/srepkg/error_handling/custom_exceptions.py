from .error_messages import SetupFileReaderError


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
