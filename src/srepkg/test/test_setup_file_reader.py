import abc
import unittest
from pathlib import Path

import src.srepkg.setup_file_reader as sfr
import src.srepkg.test.test_case_data.setup_files.sfr_expected_output as ev


class PrivateSFRTester(unittest.TestCase):

    @staticmethod
    def build_file_reader(setup_dir: Path, setup_file_type: sfr.SetupFileType):
        if setup_file_type == sfr.SetupFileType.PY:
            file_reader = sfr._SetupPyFileReader(
                setup_file=setup_dir / 'setup.py')
        elif setup_file_type == sfr.SetupFileType.CFG:
            file_reader = sfr._SetupCfgFileReader(
                setup_file=setup_dir / 'setup.cfg')

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


class MatchSrcLayoutPy(PrivateSFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'match_src_layout'
    file_type = sfr.SetupFileType.PY
    expected_vals = ev.match_src_layout_py


class MatchSrcLayoutCfg(PrivateSFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'match_src_layout'
    file_type = sfr.SetupFileType.CFG
    expected_vals = ev.match_src_layout_cfg


class MatchNonSrcLayoutPy(PrivateSFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'match_non_src_layout'
    file_type = sfr.SetupFileType.PY
    expected_vals = ev.match_non_src_layout_py


class SrcLayoutNoCfgPy(PrivateSFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'src_layout_no_cfg'
    file_type = sfr.SetupFileType.PY
    expected_vals = ev.src_layout_no_cfg_py


class SrcLayoutNoCfgCfg(PrivateSFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'src_layout_no_cfg'
    file_type = sfr.SetupFileType.CFG
    expected_vals = ev.src_layout_no_cfg_cfg


class SrcLayoutNoPyCfg(PrivateSFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'src_layout_no_py'
    file_type = sfr.SetupFileType.CFG
    expected_vals = ev.src_layout_no_py_cfg


class SrcLayoutNoPyPy(PrivateSFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'src_layout_no_py'
    file_type = sfr.SetupFileType.PY
    expected_vals = ev.src_layout_no_py_py


class MixedSrcLayoutValidPy(PrivateSFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'mixed_src_layout_valid'
    file_type = sfr.SetupFileType.PY
    expected_vals = ev.mixed_src_layout_valid_py


class MixedSrcLayoutValidCfg(PrivateSFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'mixed_src_layout_valid'
    file_type = sfr.SetupFileType.CFG
    expected_vals = ev.mixed_src_layout_valid_cfg


class MixedSrcLayoutInvalidPy(PrivateSFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'mixed_src_layout_invalid'
    file_type = sfr.SetupFileType.PY
    expected_vals = ev.mixed_src_layout_invalid_py


class MixedSrcLayoutInvalidCfg(PrivateSFRTester):
    setup_dir = Path(__file__).parent.absolute() / 'test_case_data' / \
                'setup_files' / 'mixed_src_layout_invalid'
    file_type = sfr.SetupFileType.CFG
    expected_vals = ev.mixed_src_layout_invalid_cfg


class PublicSFRTester(unittest.TestCase):
    file_types = {
        '.cfg': sfr.SetupFileType.CFG,
        '.py': sfr.SetupFileType.PY
    }

    base_path = Path(__file__).parent.absolute() / 'test_case_data' / \
        'setup_files'

    test_case_data = [
        ('file_type_only/setup.py', ev.file_type_only_py),
        ('file_type_only/setup.cfg', ev.file_type_only_cfg),
        ('match_src_layout/setup.py', ev.match_src_layout_py),
        ('match_src_layout/setup.cfg', ev.match_src_layout_cfg),
        ('match_non_src_layout/setup.py', ev.match_non_src_layout_py),
        ('match_non_src_layout/setup.cfg', ev.match_non_src_layout_cfg),
        ('src_layout_no_cfg/setup.py', ev.src_layout_no_cfg_py),
        ('src_layout_no_cfg/setup.cfg', ev.src_layout_no_cfg_cfg),
        ('src_layout_no_py/setup.py', ev.src_layout_no_py_py),
        ('src_layout_no_py/setup.cfg', ev.src_layout_no_py_cfg)
    ]

    def run_test(self, setup_file_rel_path: str, private_data: dict):
        setup_file = self.base_path / setup_file_rel_path
        public_sfr = sfr.SetupFileReader(setup_file)
        setup_info = public_sfr.get_setup_info()
        file_type = self.file_types[setup_file.suffix]
        assert setup_info == sfr.SetupFileInfo(
            **{**private_data['format_matched'], **{'file_type': file_type}})

    def test_all_cases(self):
        for test_case in self.test_case_data:
            self.run_test(test_case[0], test_case[1])


if __name__ == '__main__':
    unittest.main()
