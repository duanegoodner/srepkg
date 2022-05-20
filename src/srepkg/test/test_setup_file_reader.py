import abc
import unittest
from pathlib import Path

import src.srepkg.setup_file_reader as sfr
import src.srepkg.test.test_case_data.setup_files.sfr_expected_output as ev


class SFRTester(unittest.TestCase):

    @staticmethod
    def build_file_reader(setup_dir: Path, setup_file_type: sfr.SetupFileType):
        if setup_file_type == sfr.SetupFileType.PY:
            file_reader = sfr._SetupPyFileReader(
                setup_file=setup_dir / 'setup.py',
                file_type=setup_file_type)
        elif setup_file_type == sfr.SetupFileType.CFG:
            file_reader = sfr._SetupCfgFileReader(
                setup_file=setup_dir / 'setup.cfg',
                file_type=setup_file_type)

        return file_reader

    @property
    @abc.abstractmethod
    def setup_dir(self):
        return Path(__file__).parent.absolute() / 'test_case_data' / \
               'setup_files' / 'file_type_only'

    @property
    @abc.abstractmethod
    def file_type(self):
        return sfr.SetupFileType.PY

    @property
    @abc.abstractmethod
    def expected_vals(self):
        return ev.file_type_only_py

    def setUp(self) -> None:
        self._file_reader = self.build_file_reader(self.setup_dir,
                                                   self.file_type)

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
        setup_info = self._file_reader.get_setup_info()
        assert setup_info == sfr.SetupFileInfo(
            **{**self.expected_vals['format_matched'],
                **{'file_type': self.file_type}})


class MatchSrcLayoutPy(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'match_src_layout'
    file_type = sfr.SetupFileType.PY
    expected_vals = ev.match_src_layout_py


class MatchSrcLayoutCfg(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'match_src_layout'
    file_type = sfr.SetupFileType.CFG
    expected_vals = ev.match_src_layout_cfg


class MatchNonSrcLayoutPy(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'match_non_src_layout'
    file_type = sfr.SetupFileType.PY
    expected_vals = ev.match_non_src_layout_py


class SrcLayoutNoCfgPy(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'src_layout_no_cfg'
    file_type = sfr.SetupFileType.PY
    expected_vals = ev.src_layout_no_cfg_py


class SrcLayoutNoCfgCfg(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'src_layout_no_cfg'
    file_type = sfr.SetupFileType.CFG
    expected_vals = ev.src_layout_no_cfg_cfg


class SrcLayoutNoPyCfg(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'src_layout_no_py'
    file_type = sfr.SetupFileType.CFG
    expected_vals = ev.src_layout_no_py_cfg


class SrcLayoutNoPyPy(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'src_layout_no_py'
    file_type = sfr.SetupFileType.PY
    expected_vals = ev.src_layout_no_py_py


class MixedSrcLayoutValidPy(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'mixed_src_layout_valid'
    file_type = sfr.SetupFileType.PY
    expected_vals = ev.mixed_src_layout_valid_py


class MixedSrcLayoutValidCfg(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'mixed_src_layout_valid'
    file_type = sfr.SetupFileType.CFG
    expected_vals = ev.mixed_src_layout_valid_cfg


class MixedSrcLayoutInvalidPy(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'mixed_src_layout_invalid'
    file_type = sfr.SetupFileType.PY
    expected_vals = ev.mixed_src_layout_invalid_py


class MixedSrcLayoutInvalidCfg(SFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'mixed_src_layout_invalid'
    file_type = sfr.SetupFileType.CFG
    expected_vals = ev.mixed_src_layout_invalid_cfg


if __name__ == '__main__':
    unittest.main()
