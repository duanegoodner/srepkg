import pytest
from pathlib import Path
from typing import NamedTuple
import srepkg.utils.dist_archive_file_tools as daft
import srepkg.utils.cd_context_manager as cdcm
import srepkg.utils.pkg_type_identifier as pti
import srepkg.error_handling.custom_exceptions as ce


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
            file_name="testproj-0.0.0.tar.gz",
            file_type=daft.ArchiveFileType.TAR_GZ,
            dist_type=daft.ArchiveDistType.SDIST,
        ),
        ExpectedFileDistType(
            file_name="testproj-0.0.0.zip",
            file_type=daft.ArchiveFileType.ZIP,
            dist_type=daft.ArchiveDistType.SDIST,
        ),
        ExpectedFileDistType(
            file_name="testproj-0.0.0-py3-none-any.whl",
            file_type=daft.ArchiveFileType.WHL,
            dist_type=daft.ArchiveDistType.WHEEL,
        ),
        ExpectedFileDistType(
            file_name="testproj-0.0.0-not-a-distribution.py",
            file_type=daft.ArchiveFileType.UNKNOWN,
            dist_type=daft.ArchiveDistType.UNKNOWN,
        ),
    ]

    identifier = daft.ArchiveIdentifier()
    test_cases_path = Path(__file__).parent.absolute() / "package_test_cases"

    def run_file_and_dist_id_test(self, info: ExpectedFileDistType):
        assert (
            self.identifier.id_file_type(self.test_cases_path / info.file_name)
            == info.file_type
        )
        assert (
            self.identifier.id_dist_type(self.test_cases_path / info.file_name)
            == info.dist_type
        )

    def test_all_expected_info(self):
        for test_case in self.expected_id_info:
            self.run_file_and_dist_id_test(test_case)


class TestCompressedFileExtractor:
    test_cases_path = Path(__file__).parent.absolute() / "package_test_cases"

    archive_filenames = [
        "testproj-0.0.0.tar.gz",
        "testproj-0.0.0.zip",
        "testproj-0.0.0-py3-none-any.whl",
    ]

    extractor = daft.CompressedFileExtractor()

    def run_expected_good_extraction(self, file_name: str, output_dir: Path):
        self.extractor.extract(self.test_cases_path / file_name, output_dir)
        assert (output_dir / "testproj-0.0.0").exists()

    def test_expected_good_extractions(self, tmp_path):
        for file_name in self.archive_filenames:
            self.run_expected_good_extraction(file_name, tmp_path)

    def test_bad_extraction(self, tmp_path):
        with pytest.raises(ce.UnsupportedCompressionType):
            self.extractor.extract(
                self.test_cases_path / "testproj-0.0.0-not-a-distribution.py",
                tmp_path,
            )


class BrokenPkgRefIdentifier(pti.PkgRefIdentifier):
    def _check_all_types(self):
        return {
            pti.PkgRefType.LOCAL_SRC_NONGIT: True,
            pti.PkgRefType.LOCAL_SDIST: True,
            pti.PkgRefType.LOCAL_WHEEL: True,
            pti.PkgRefType.PYPI_PKG: True,
            pti.PkgRefType.GIT_REPO: True,
        }


class TestPkgRefIdentifier:
    local_test_pkgs_path = (
        Path(__file__).parent.absolute() / "package_test_cases"
    )

    def test_bad_pkg_ref(self):
        pkg_ref_identifier = pti.PkgRefIdentifier("bad_ref")
        pkg_ref_type = pkg_ref_identifier.identify()
        assert pkg_ref_type == pti.PkgRefType.UNKNOWN
        # with pytest.raises(SystemExit):
        #     pkg_ref_identifier.identify()

    def test_multiple_possible_types(self):
        pkg_ref_identifier = BrokenPkgRefIdentifier(
            orig_pkg_ref=str(self.local_test_pkgs_path / "testproj")
        )
        pkg_ref_type = pkg_ref_identifier.identify()
        assert pkg_ref_type == pti.PkgRefType.MULTIPLE_POSSIBLE
