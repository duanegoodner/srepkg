import pytest
import srepkg.utils.dist_archive_file_tools as daft
import srepkg.utils.cd_context_manager as cdcm
from pathlib import Path
from typing import NamedTuple


def test_dir_change_to(tmp_path):
    cwd = Path.cwd()
    assert cwd != tmp_path

    with cdcm.dir_change_to(tmp_path):
        assert Path.cwd() == tmp_path

    assert Path.cwd() == cwd


class ExpectedFileDistType(NamedTuple):
    file_name: str
    file_type: daft.ArchiveFileType
    dist_type: daft.ArchiveDistType


class TestArchiveIdentifier:
    expected_id_info = [
        ExpectedFileDistType(
            file_name='testproj-0.0.0.tar.gz',
            file_type=daft.ArchiveFileType.TAR_GZ,
            dist_type=daft.ArchiveDistType.SDIST
        ),
        ExpectedFileDistType(
            file_name='testproj-0.0.0.zip',
            file_type=daft.ArchiveFileType.ZIP,
            dist_type=daft.ArchiveDistType.SDIST
        ),
        ExpectedFileDistType(
            file_name='testproj-0.0.0-py3-none-any.whl',
            file_type=daft.ArchiveFileType.WHL,
            dist_type=daft.ArchiveDistType.WHEEL
        ),
        ExpectedFileDistType(
            file_name='testproj-0.0.0-not-a-distribution.py',
            file_type=daft.ArchiveFileType.UNKNOWN,
            dist_type=daft.ArchiveDistType.UNKNOWN
        )
    ]

    identifier = daft.ArchiveIdentifier()
    test_cases_path = Path(__file__).parent.absolute() / \
        'package_test_cases'

    def run_file_and_dist_id_test(self, info: ExpectedFileDistType):
        assert self.identifier.id_file_type(
            self.test_cases_path / info.file_name) == info.file_type
        assert self.identifier.id_dist_type(
            self.test_cases_path / info.file_name) == info.dist_type

    def test_all_expected_info(self):
        for test_case in self.expected_id_info:
            self.run_file_and_dist_id_test(test_case)


# class TestCompressedFileExtractor:
#
#     extractor = daft.CompressedFileExtractor()
#