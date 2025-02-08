import subprocess
import zipfile
import tarfile
from enum import Enum, auto
from pathlib import Path
import srepkg.error_handling.custom_exceptions as ce
import srepkg.utils.logged_err_detecting_subprocess as leds
from srepkg.error_handling.custom_exceptions import UnsupportedCompressionType


class ArchiveFileType(Enum):
    TAR_GZ = auto()
    ZIP = auto()
    WHL = auto()
    UNKNOWN = auto()


class ArchiveDistType(Enum):
    SDIST = auto()
    WHEEL = auto()
    UNKNOWN = auto()


# https://stackoverflow.com/a/13044946/17979376
# https://stackoverflow.com/a/63404232/17979376
class ArchiveIdentifier:
    file_signatures = {
        b"\x1f\x8b\x08": ArchiveFileType.TAR_GZ,
        b"\x50\x4b\x03\x04": ArchiveFileType.ZIP,
    }

    dist_file_table = {
        ArchiveFileType.TAR_GZ: ArchiveDistType.SDIST,
        ArchiveFileType.ZIP: ArchiveDistType.SDIST,
        ArchiveFileType.WHL: ArchiveDistType.WHEEL,
        ArchiveFileType.UNKNOWN: ArchiveDistType.UNKNOWN,
    }

    def id_file_type(self, possible_archive: Path):
        max_len = max(len(x) for x in self.file_signatures)

        with possible_archive.open(mode="rb") as f:
            file_start = f.read(max_len)
        for signature, filetype in self.file_signatures.items():
            if file_start.startswith(signature):
                archive_filetype = filetype
                # .whl files are special case of .zip
                if (
                    filetype == archive_filetype.ZIP
                    and possible_archive.suffix == ".whl"
                ):
                    archive_filetype = filetype.WHL
                return archive_filetype

        return ArchiveFileType.UNKNOWN

    def id_dist_type(self, possible_archive: Path):
        return self.dist_file_table[self.id_file_type(possible_archive)]


class CompressedFileExtractor:

    @staticmethod
    def _extract_zip(compressed_file: Path, output_dir: Path):
        with zipfile.ZipFile(compressed_file, "r") as zf:
            zf.extractall(output_dir)

    @staticmethod
    def _extract_tar_gz(compressed_file: Path, output_dir: Path):
        with tarfile.open(compressed_file) as tf:
            tf.extractall(output_dir)

    @staticmethod
    def _extract_whl(compressed_file: Path, output_dir: Path):
        # TODO replace with leds.LoggedErrDetectingSubprocess
        # subprocess.call(
        #     ['wheel', 'unpack', str(compressed_file), '--dest',
        #      str(output_dir)])

        leds.LoggedErrDetectingSubprocess(
            cmd=[
                "wheel",
                "unpack",
                str(compressed_file),
                "--dest",
                str(output_dir),
            ],
            gen_logger_name=__name__,
            std_out_logger_name="std_out",
            std_err_logger_name="std_err",
            default_exception=ce.WheelUnpackError,
        )

    @staticmethod
    def _extract_unknown(compressed_file: Path, output_dir: Path):
        raise UnsupportedCompressionType(str(compressed_file))

    @property
    def _dispatch_method(self):
        return {
            ArchiveFileType.ZIP: self._extract_zip,
            ArchiveFileType.TAR_GZ: self._extract_tar_gz,
            ArchiveFileType.WHL: self._extract_whl,
            ArchiveFileType.UNKNOWN: self._extract_unknown,
        }

    def extract(self, compressed_file: Path, output_dir: Path):
        file_type = ArchiveIdentifier().id_file_type(compressed_file)

        self._dispatch_method[file_type](compressed_file, output_dir)


# targz_file_type = ArchiveIdentifier().id_file_type(
#     Path('/Users/duane/dproj/testproj/dist/testproj-0.0.0.tar.gz')
# )
#
# zip_file_type = ArchiveIdentifier().id_file_type(
#     Path('/Users/duane/dproj/testproj/dist/testproj-0.0.0.zip')
# )
#
# whl_file_type = ArchiveIdentifier().id_file_type(
#     Path('/Users/duane/dproj/testproj/dist/testproj-0.0.0.zip')
# )
#
# print(targz_file_type)
# print(zip_file_type)
# print(whl_file_type)
