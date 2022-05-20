import abc
import unittest

import src.srepkg.setup_file_reader as sfr
import src.srepkg.test.test_case_data.setup_files.sfr_expected_output as sfeo
import src.srepkg.test.test_case_data.setup_files.si_expected_output as sieo


class SetupInfoTester(unittest.TestCase):

    @property
    @abc.abstractmethod
    def py_data(self):
        return sfeo.file_type_only_py['final_data']

    @property
    @abc.abstractmethod
    def cfg_data(self):
        return sfeo.file_type_only_cfg['final_data']

    @property
    @abc.abstractmethod
    def expected_out(self):
        return sieo.file_type_only

    def setUp(self) -> None:
        self._py_setup_info = sfr.SetupFileInfo(**self.py_data)
        self._cfg_setup_info = sfr.SetupFileInfo(**self.cfg_data)

    def attribute_check(self, stage: str, file_type: str):
        expected_vals = self.expected_out[stage][file_type]
        found_info = getattr(self, '_' + file_type + '_setup_info')

        assert found_info._console_scripts == expected_vals['console_scripts']
        assert found_info._file_type == expected_vals['file_type']
        assert found_info._package_dir == expected_vals['package_dir']
        assert found_info._name == expected_vals['name']

    def test_init_py(self):
        self.attribute_check('init', 'py')

    def test_init_cfg(self):
        self.attribute_check('init', 'cfg')


class MatchSrcSetupInfoTester(SetupInfoTester):
    py_data = sfeo.match_src_layout_py['final_data']
    cfg_data = sfeo.match_src_layout_cfg['final_data']
    expected_out = sieo.match_src_layout


class MatchNonSrcSetupInfoTester(SetupInfoTester):
    py_data = sfeo.match_non_src_layout_py['final_data']
    cfg_data = sfeo.match_non_src_layout_cfg['final_data']
    expected_out = sieo.match_non_src_layout


class SrcNoCfgSetupInfoTester(SetupInfoTester):
    py_data = sfeo.src_layout_no_cfg_py['final_data']
    cfg_data = sfeo.src_layout_no_cfg_cfg['final_data']
    expected_out = sieo.src_layout_no_cfg


class SrcNoPySetupInfoTester(SetupInfoTester):
    py_data = sfeo.src_layout_no_py_py['final_data']
    cfg_data = sfeo.src_layout_no_py_cfg['final_data']
    expected_out = sieo.src_layout_no_py


class MixedSrcLayoutValidSetupInfoTester(SetupInfoTester):
    py_data = sfeo.mixed_src_layout_valid_py['final_data']
    cfg_data = sfeo.mixed_src_layout_valid_cfg['final_data']
    expected_out = sieo.mixed_src_valid




