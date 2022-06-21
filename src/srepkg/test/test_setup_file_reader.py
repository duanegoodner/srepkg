import abc
import unittest
from pathlib import Path

import srepkg.setup_file_reader as sfr
import srepkg.test.sfr_valid_cases.sfr_expected_output as ev


class PrivateSFRTester(unittest.TestCase):

    @staticmethod
    def build_file_reader(setup_dir: Path, setup_file_type: str):
        if setup_file_type == '.py':
            file_reader = sfr._SetupPyFileReader(
                setup_file=setup_dir / 'setup.py')
        elif setup_file_type == '.cfg':
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
        return '.py'

    @property
    def base_dir(self):
        return Path(__file__).parent.absolute() /\
               'sfr_valid_cases'

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

        assert setup_info == ev.get_final_data(self.expected_vals)


class MatchSrcLayoutPy(PrivateSFRTester):
    dataset_name = 'match_src_layout'
    file_type = '.py'


class MatchSrcLayoutCfg(PrivateSFRTester):
    dataset_name = 'match_src_layout'
    file_type = '.cfg'


class MatchNonSrcLayoutPy(PrivateSFRTester):
    dataset_name = 'match_non_src_layout'
    file_type = '.py'


class SrcLayoutNoCfgPy(PrivateSFRTester):
    dataset_name = 'src_layout_no_cfg'
    file_type = '.py'


class SrcLayoutNoCfgCfg(PrivateSFRTester):
    dataset_name = 'src_layout_no_cfg'
    file_type = '.cfg'


class SrcLayoutNoPyCfg(PrivateSFRTester):
    dataset_name = 'src_layout_no_py'
    file_type = '.cfg'


class SrcLayoutNoPyPy(PrivateSFRTester):
    dataset_name = 'src_layout_no_py'
    file_type = '.py'


class MixedSrcLayoutValidPy(PrivateSFRTester):
    dataset_name = 'mixed_src_layout_valid'
    file_type = '.py'


class MixedSrcLayoutValidCfg(PrivateSFRTester):
    dataset_name = 'mixed_src_layout_valid'
    file_type = '.cfg'


class MixedSrcLayoutCSEOverride(PrivateSFRTester):
    dataset_name = 'mixed_src_layout_cse_override'
    file_type = '.py'


class PublicSFRTester(unittest.TestCase):
    file_types = {
        '.cfg': '.cfg',
        '.py': '.py'
    }

    base_path = Path(__file__).parent.absolute() /\
        'sfr_valid_cases'

    test_case_data = [
        ('file_type_only', ev.file_type_only),
        ('match_src_layout', ev.match_src_layout),
        ('match_non_src_layout', ev.match_non_src_layout),
        ('src_layout_no_cfg', ev.src_layout_no_cfg),
        ('src_layout_no_py', ev.src_layout_no_py),
    ]

    def run_test(self, dataset_name: str, private_data: dict):
        cfg_setup_file = self.base_path / dataset_name / 'setup.cfg'
        py_setup_file = self.base_path / dataset_name / 'setup.py'

        public_sfr_cfg = sfr.SetupFileReader(cfg_setup_file)
        public_sfr_py = sfr.SetupFileReader(py_setup_file)
        cfg_setup_info = public_sfr_cfg.get_setup_info()
        py_setup_info = public_sfr_py.get_setup_info()
        assert cfg_setup_info == ev.get_final_data(private_data['.cfg'])
        assert py_setup_info == ev.get_final_data(private_data['.py'])

    def test_all_cases(self):
        for test_case in self.test_case_data:
            self.run_test(test_case[0], test_case[1])


if __name__ == '__main__':
    unittest.main()
