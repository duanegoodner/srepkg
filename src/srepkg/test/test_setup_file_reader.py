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
    def dataset_name(self) -> str:
        return 'file_type_only'

    @property
    @abc.abstractmethod
    def file_type(self):
        return sfr.SetupFileType.PY

    @property
    def base_dir(self):
        return Path(__file__).parent.absolute() / 'test_case_data' / \
               'setup_files'

    @property
    def setup_dir(self):
        return self.base_dir / self.dataset_name

    @property
    def expected_vals(self):
        return getattr(ev, self.dataset_name)[self.file_type]

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
        assert setup_info == self.expected_vals['format_matched']


class MatchSrcLayoutPy(PrivateSFRTester):
    dataset_name = 'match_src_layout'
    file_type = sfr.SetupFileType.PY


class MatchSrcLayoutCfg(PrivateSFRTester):
    dataset_name = 'match_src_layout'
    file_type = sfr.SetupFileType.CFG


class MatchNonSrcLayoutPy(PrivateSFRTester):
    dataset_name = 'match_non_src_layout'
    file_type = sfr.SetupFileType.PY


class SrcLayoutNoCfgPy(PrivateSFRTester):
    dataset_name = 'src_layout_no_cfg'
    file_type = sfr.SetupFileType.PY


class SrcLayoutNoCfgCfg(PrivateSFRTester):
    dataset_name = 'src_layout_no_cfg'
    file_type = sfr.SetupFileType.CFG


class SrcLayoutNoPyCfg(PrivateSFRTester):
    dataset_name = 'src_layout_no_py'
    file_type = sfr.SetupFileType.CFG


class SrcLayoutNoPyPy(PrivateSFRTester):
    dataset_name = 'src_layout_no_py'
    file_type = sfr.SetupFileType.PY


class MixedSrcLayoutValidPy(PrivateSFRTester):
    dataset_name = 'mixed_src_layout_valid'
    file_type = sfr.SetupFileType.PY


class MixedSrcLayoutValidCfg(PrivateSFRTester):
    dataset_name = 'mixed_src_layout_valid'
    file_type = sfr.SetupFileType.CFG


class MixedSrcLayoutInvalidPy(PrivateSFRTester):
    dataset_name = 'mixed_src_layout_invalid'
    file_type = sfr.SetupFileType.PY


class MixedSrcLayoutInvalidCfg(PrivateSFRTester):
    dataset_name = 'mixed_src_layout_invalid'
    file_type = sfr.SetupFileType.CFG


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
        assert setup_info == private_data['format_matched']

    def test_all_cases(self):
        for test_case in self.test_case_data:
            self.run_test(test_case[0], test_case[1])


if __name__ == '__main__':
    unittest.main()
