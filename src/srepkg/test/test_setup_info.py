import abc
import unittest

import src.srepkg.setup_file_reader as sfr
import src.srepkg.test.test_case_data.setup_files.sfr_expected_output as sfeo
import src.srepkg.test.test_case_data.setup_files.si_expected_output as sieo


class SetupInfoTester(unittest.TestCase):

    @property
    @abc.abstractmethod
    def dataset_name(self) -> str:
        return 'file_type_only'

    @property
    def py_data(self):
        return getattr(
            sfeo,
            self.dataset_name
        )[sfr.SetupFileType.PY]['format_matched']

    @property
    def cfg_data(self):
        return getattr(
            sfeo,
            self.dataset_name
        )[sfr.SetupFileType.CFG]['format_matched']

    @property
    def expected_out(self):
        return getattr(sieo, self.dataset_name)

    def setUp(self) -> None:
        self._setup_info = {
            sfr.SetupFileType.PY: sfr.SetupFileInfo(**self.py_data),
            sfr.SetupFileType.CFG: sfr.SetupFileInfo(**self.cfg_data)
        }

    def attribute_check(self, stage: str, file_type: sfr.SetupFileType):
        expected_vals = self.expected_out[stage][file_type]
        found_info = self._setup_info[file_type]

        assert found_info._console_scripts == expected_vals['console_scripts']
        assert found_info._package_dir == expected_vals['package_dir']
        assert found_info._name == expected_vals['name']

    def test_init_py(self):
        self.attribute_check('init', sfr.SetupFileType.PY)

    def test_init_cfg(self):
        self.attribute_check('init', sfr.SetupFileType.CFG)


class MatchSrcSetupInfoTester(SetupInfoTester):
    dataset_name = 'match_src_layout'


class MatchNonSrcSetupInfoTester(SetupInfoTester):
    dataset_name = 'match_non_src_layout'


class SrcNoCfgSetupInfoTester(SetupInfoTester):
    dataset_name = 'src_layout_no_cfg'


class SrcNoPySetupInfoTester(SetupInfoTester):
    dataset_name = 'src_layout_no_py'


class MixedSrcLayoutValidSetupInfoTester(SetupInfoTester):
    dataset_name = 'mixed_src_layout_valid'
