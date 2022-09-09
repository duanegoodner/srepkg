import hashlib
import logging
import subprocess
import sys
import tempfile
from pathlib import Path
import srepkg.dist_builder_sub_process as dbs
import srepkg.utils.logged_err_detecting_subprocess as leds


class DistBuilder:

    def __init__(
            self,
            distribution: str,
            srcdir: Path,
            output_directory: Path,
            std_out_file: Path = tempfile.TemporaryFile(),
            std_err_file: Path = tempfile.TemporaryFile()):
        self._distribution = distribution
        self._srcdir = srcdir
        self._output_directory = output_directory
        self._std_out_file = std_out_file
        self._std_err_file = std_err_file

    @staticmethod
    def _calc_md5(file_path: Path):
        hash_md5 = hashlib.md5()
        with file_path.open(mode="rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    @property
    def _files_in_dest_dir(self):
        return [
            item for item in self._output_directory.iterdir() if not
            item.is_dir()
        ]

    def build(self):
        orig_dest_checksums = [
            self._calc_md5(item) for item in self._files_in_dest_dir
        ]

        leds.LoggedErrDetectingSubprocess(
            cmd=[
                sys.executable, dbs.__file__,
                self._distribution,
                str(self._srcdir),
                str(self._output_directory)
            ],
            gen_logger_name=__name__,
            std_out_logger_name="std_out",
            std_err_logger_name="std_err",
            default_exception=BuildSubprocessError
        ).run()

        new_wheel_files = [
            item for item in self._files_in_dest_dir if
            (self._calc_md5(item) not in orig_dest_checksums and
             item.suffix == ".whl")]

        logging.getLogger(__name__).debug(str(new_wheel_files))
        logging.getLogger(__name__).debug(str(self._files_in_dest_dir))
        assert len(new_wheel_files) == 1

        return new_wheel_files[0]


class BuildSubprocessError(Exception):
    def __init__(
            self,
            sub_process: subprocess.CompletedProcess,
            msg="Error occurred when running subprocess intended build a sdist"
                " or wheel."):
        self._sub_process = sub_process
        self._msg = msg

    def __str__(self):
        return f"{str(self._sub_process)} -> {self._msg}"
