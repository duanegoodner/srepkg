import unittest
from pathlib import Path

import src.srepkg.orig_pkg_inspector as opi
import src.srepkg.test.test_case_data.setup_file_reader.expected_vals as ev


class SetupFileReaderBasic(unittest.TestCase):
    _setup_files_path = Path(__file__).parent.absolute() / 'test_case_data' / \
                        'setup_file_reader' / 'testproj_matched'

    _cfg_keys = opi.SetupKeys(
        single_level=[],
        two_level=[('metadata', 'name'), ('options', 'package_dir'),
                   ('options.entry_points', 'console_scripts')])

    _py_keys = opi.SetupKeys(single_level=['name', 'package_dir', 'dummy'],
                             two_level=[('entry_points', 'console_scripts')])

    _expected_vals = ev.testproj_matched

    def setUp(self) -> None:
        self._my_file_reader = opi.SetupFilesReader(
            self._setup_files_path,
            cfg_keys=self._cfg_keys,
            py_keys=self._py_keys)

    def test_read_raw_setup_py(self):
        self._my_file_reader._read_raw_setup_py()
        assert self._my_file_reader._setup_data.py ==\
               self._expected_vals['py_raw']

    def test_read_raw_setup_cfg(self):
        self._my_file_reader._read_raw_setup_cfg()
        assert self._my_file_reader._setup_data.cfg ==\
               self._expected_vals['cfg_raw']

    def test_filter_all_setup_data(self):
        self._my_file_reader._read_raw_setup_py()
        self._my_file_reader._read_raw_setup_cfg()
        self._my_file_reader._filter_all_setup_data()
        assert self._my_file_reader._setup_data.py ==\
               self._expected_vals['py_filtered']
        assert self._my_file_reader._setup_data.cfg ==\
               self._expected_vals['cfg_filtered']

    def test_reformat_cfg_pkg_dir(self):
        self._my_file_reader._read_raw_setup_py()
        self._my_file_reader._read_raw_setup_cfg()
        self._my_file_reader._filter_all_setup_data()
        self._my_file_reader._cfg_cs_str_to_list()
        self._my_file_reader._cfg_pkg_dir_str_to_list()
        assert self._my_file_reader._setup_data.cfg ==\
               self._expected_vals['cfg_format_matched']

    def test_cs_string_to_cse(self):
        self._my_file_reader._read_raw_setup_py()
        self._my_file_reader._read_raw_setup_cfg()
        self._my_file_reader._filter_all_setup_data()
        self._my_file_reader._cfg_cs_str_to_list()
        self._my_file_reader._cfg_pkg_dir_str_to_list()
        self._my_file_reader._cs_lists_to_cse_objs()
        assert self._my_file_reader._setup_data.py ==\
               self._expected_vals['py_with_cse_objs']
        assert self._my_file_reader._setup_data.cfg ==\
               self._expected_vals['cfg_with_cse_objs']
        assert self._my_file_reader._setup_data.py ==\
               self._my_file_reader._setup_data.cfg

    def test_get_setup_params(self):
        setup_params = self._my_file_reader.get_setup_params()
        assert setup_params == self._expected_vals['merged_params']


