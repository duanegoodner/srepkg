from enum import Enum, auto
from pathlib import Path


# https://stackoverflow.com/a/13044946/17979376
# https://stackoverflow.com/a/63404232/17979376


class ArchiveFileType(Enum):
    TAR_GZ = auto()
    ZIP = auto()
    UNKNOWN = auto()


class CompressedFileIdentifier:
    magic_dict = {
        b"\x1f\x8b\x08": ArchiveFileType.TAR_GZ,
        b"\x50\x4b\x03\x04": ArchiveFileType.ZIP
    }

    max_len = max(len(x) for x in magic_dict)

    def identify_compression_type(self, comp_file: Path):
        with comp_file.open(mode='rb') as f:
            file_start = f.read(self.max_len)
        for magic, filetype in self.magic_dict.items():
            if file_start.startswith(magic):
                return filetype

        return ArchiveFileType.UNKNOWN


targz_file_type = CompressedFileIdentifier().identify_compression_type(
    Path('/Users/duane/dproj/testproj/dist/testproj-0.0.0.tar.gz')
)

zip_file_type = CompressedFileIdentifier().identify_compression_type(
    Path('/Users/duane/dproj/testproj/dist/testproj-0.0.0.zip')
)

whl_file_type = CompressedFileIdentifier().identify_compression_type(
    Path('/Users/duane/dproj/testproj/dist/testproj-0.0.0.zip')
)

print(targz_file_type)
print(zip_file_type)
print(whl_file_type)






