import abc
import unittest
from enum import Enum, auto
from pathlib import Path

import src.srepkg.setup_file_reader as sfr
import src.srepkg.test.test_case_data.setup_files.expected_vals as ev


class SetupFileType(Enum):
    PY = auto()
    CFG = auto()


def build_file_reader(setup_dir: Path, setup_file_type: SetupFileType):
    if setup_file_type == SetupFileType.PY:
        file_reader = sfr.SetupPyFileReader(
            setup_file=setup_dir / 'setup.py',
            doi_keys=sfr.SetupKeys(
                single_level=['name', 'package_dir', 'dummy'],
                two_level=[('entry_points', 'console_scripts')]))
    elif setup_file_type == SetupFileType.CFG:
        file_reader = sfr.SetupCfgFileReader(
            setup_file=setup_dir / 'setup.cfg',
            doi_keys=sfr.SetupKeys(single_level=[],
                                   two_level=[('metadata', 'name'),
                                              ('options', 'package_dir'),
                                              ('options.entry_points',
                                               'console_scripts')]))

    return file_reader


class SFRTester(unittest.TestCase, abc.ABC):

    @property
    @abc.abstractmethod
    def setup_dir(self):
        pass

    @property
    @abc.abstractmethod
    def file_type(self):
        pass

    @property
    @abc.abstractmethod
    def expected_vals(self):
        pass

    def setUp(self) -> None:
        self._file_reader = build_file_reader(self.setup_dir, self.file_type)

    def test_read_raw(self):
        self._file_reader._read_raw_data()
        assert self._file_reader._data == self.expected_vals['raw']

    def test_filter(self):
        self._file_reader._read_raw_data()._filter_raw_data()
        assert self._file_reader._data == self.expected_vals['filtered']

    def test_format_matched(self):
        self._file_reader._read_raw_data()._filter_raw_data() \
            ._match_to_py_format()
        assert self._file_reader._data == self.expected_vals['format_matched']

    def test_get_data(self):
        collected_data = self._file_reader.get_data()
        assert collected_data == self.expected_vals['format_matched']


class MatchSrcLayoutPy(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'match_src_layout'
    file_type = SetupFileType.PY
    expected_vals = ev.match_src_layout_py


class MatchSrcLayoutCfg(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'match_src_layout'
    file_type = SetupFileType.CFG
    expected_vals = ev.match_src_layout_cfg


class MatchNonSrcLayoutPy(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'match_non_src_layout'
    file_type = SetupFileType.PY
    expected_vals = ev.match_non_src_layout_py


class SrcLayoutNoCfgPy(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'src_layout_no_cfg'
    file_type = SetupFileType.PY
    expected_vals = ev.src_layout_no_cfg_py


class SrcLayoutNoCfgCfg(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'src_layout_no_cfg'
    file_type = SetupFileType.CFG
    expected_vals = ev.src_layout_no_cfg_cfg


class SrcLayoutNoPyCfg(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'src_layout_no_py'
    file_type = SetupFileType.CFG
    expected_vals = ev.src_layout_no_py_cfg


class SrcLayoutNoPyPy(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'src_layout_no_py'
    file_type = SetupFileType.PY
    expected_vals = ev.src_layout_no_py_py


class MixedSrcLayoutValidPy(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'mixed_src_layout_valid'
    file_type = SetupFileType.PY
    expected_vals = ev.mixed_src_layout_valid_py


class MixedSrcLayoutValidCfg(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'mixed_src_layout_valid'
    file_type = SetupFileType.CFG
    expected_vals = ev.mixed_src_layout_valid_cfg


class MixedSrcLayoutInvalidPy(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'mixed_src_layout_invalid'
    file_type = SetupFileType.PY
    expected_vals = ev.mixed_src_layout_invalid_py


class MixedSrcLayoutInvalidCfg(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'mixed_src_layout_invalid'
    file_type = SetupFileType.CFG
    expected_vals = ev.mixed_src_layout_invalid_cfg



