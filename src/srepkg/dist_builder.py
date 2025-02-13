import hashlib
import sys
import tempfile
from pathlib import Path
import srepkg.dist_builder_sub_process as dbs
import srepkg.error_handling.custom_exceptions as ce
import srepkg.utils.logged_err_detecting_subprocess as leds
import srepkg.utils.pkg_type_identifier as pti


class DistBuilder:

    def __init__(
        self,
        distribution: str,
        source_dir: Path,
        output_directory: Path,
        std_out_file: Path = tempfile.TemporaryFile(),
        std_err_file: Path = tempfile.TemporaryFile(),
    ):
        self._distribution = distribution
        self._source_dir = source_dir
        self._output_directory = output_directory
        self._output_directory.mkdir(parents=True, exist_ok=True)
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
            item
            for item in self._output_directory.iterdir()
            if not item.is_dir()
        ]

    def build(self):
        orig_dest_checksums = [
            self._calc_md5(item) for item in self._files_in_dest_dir
        ]

        leds.LoggedErrDetectingSubprocess(
            cmd=[
                sys.executable,
                dbs.__file__,
                self._distribution,
                str(self._source_dir),
                str(self._output_directory),
            ],
            gen_logger_name=__name__,
            std_out_logger_name="std_out",
            std_err_logger_name="std_err",
            default_exception=ce.BuildSubprocessError,
        ).run()

        new_dist_files = [
            item
            for item in self._files_in_dest_dir
            if (
                self._calc_md5(item) not in orig_dest_checksums
                and (
                    pti.PkgRefIdentifier(str(item)).identify_for_osp_dispatch()
                    == pti.PkgRefType.LOCAL_DIST
                )
            )
        ]
        assert len(new_dist_files) == 1

        return new_dist_files[0]
