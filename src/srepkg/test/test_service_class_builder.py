import srepkg.shared_data_structures.new_data_structures as nds
import srepkg.service_builder as sb
from pathlib import Path
from typing import NamedTuple
import pytest


class TestConstructionDirDispatch:
    dispatch = sb.ConstructionDirDispatch()

    def test_none_create_arg(self):
        construction_dir = self.dispatch.create(None)
        assert type(construction_dir).__name__ == 'TempConstructionDir'

    def test_string_create_arg(self, tmp_path):
        construction_dir = self.dispatch.create(str(tmp_path))
        assert type(construction_dir).__name__ == 'CustomConstructionDir'

    def test_path_create_arg(self, tmp_path):
        construction_dir = self.dispatch.create(tmp_path)
        assert type(construction_dir).__name__ == 'CustomConstructionDir'


class RetrieverDistProviderDispatchTestCondition(NamedTuple):
    pkg_ref_command: str
    retriever_type: str
    dist_provider_type: str


class TestPkgRetrieverAndDistProviderDispatch:
    construction_dir_dispatch = sb.ConstructionDirDispatch()
    construction_dir = construction_dir_dispatch.create(None)
    pkg_retriever_dispatch = sb.PkgRetrieverDispatch()
    dist_provider_dispatch = sb.DistProviderDispatch()

    package_test_cases = Path(__file__).parent.absolute() / 'package_test_cases'

    test_conditions = [
        RetrieverDistProviderDispatchTestCondition(
            pkg_ref_command=str(Path(package_test_cases) / 'testproj'),
            retriever_type='NullPkgRetriever',
            dist_provider_type='WheelAndSdistProvider'
        ),
        RetrieverDistProviderDispatchTestCondition(
            pkg_ref_command=str(
                Path(package_test_cases) / 'testproj-0.0.0.tar.gz'),
            retriever_type='NullPkgRetriever',
            dist_provider_type='DistCopyProvider'),
        RetrieverDistProviderDispatchTestCondition(
            pkg_ref_command=str(
                Path(package_test_cases) / 'testproj-0.0.0.zip'),
            retriever_type='NullPkgRetriever',
            dist_provider_type='DistCopyProvider'),
        RetrieverDistProviderDispatchTestCondition(
            pkg_ref_command=str(
                Path(package_test_cases) / 'testproj-0.0.0-py3-none-any.whl'),
            retriever_type='NullPkgRetriever',
            dist_provider_type='DistCopyProvider'),
        RetrieverDistProviderDispatchTestCondition(
            pkg_ref_command='black',
            retriever_type='PyPIPkgRetriever',
            dist_provider_type='NullDistProvider'),
        RetrieverDistProviderDispatchTestCondition(
            pkg_ref_command='https://github.com/psf/black',
            retriever_type='GithubPkgRetriever',
            dist_provider_type='WheelAndSdistProvider')
    ]

    def run_test_condition(
            self,
            test_condition: RetrieverDistProviderDispatchTestCondition):
        pkg_retriever = self.pkg_retriever_dispatch.create(
            test_condition.pkg_ref_command, self.construction_dir)
        dist_provider = self.dist_provider_dispatch.create(
            test_condition.pkg_ref_command, self.construction_dir)

        assert type(pkg_retriever).__name__ == test_condition.retriever_type
        assert type(dist_provider).__name__ == test_condition.dist_provider_type

    def test_all_conditions(self):
        for condition in self.test_conditions:
            self.run_test_condition(condition)


class OrigSrcPreparerTestCondition(NamedTuple):
    orig_pkg_ref_command: str
    retriever_type: str
    provider_type: str


class TestOrigSrcPreparerBuilder:

    local_test_pkgs_path = Path(__file__).parent.absolute() /\
                           'package_test_cases'

    test_conditions = {
        '01': OrigSrcPreparerTestCondition(
           orig_pkg_ref_command=str(local_test_pkgs_path / 'testproj'),
           retriever_type='NullPkgRetriever',
           provider_type='WheelAndSdistProvider'
        ),
        '02': OrigSrcPreparerTestCondition(
            orig_pkg_ref_command=str(
                local_test_pkgs_path / 'testproj-0.0.0.tar.gz'),
            retriever_type='NullPkgRetriever',
            provider_type='DistCopyProvider'
        ),
        '03': OrigSrcPreparerTestCondition(
            orig_pkg_ref_command=str(
                local_test_pkgs_path / 'testproj-0.0.0.zip'),
            retriever_type='NullPkgRetriever',
            provider_type='DistCopyProvider'
        ),
        '04': OrigSrcPreparerTestCondition(
            orig_pkg_ref_command=str(
                local_test_pkgs_path / 'testproj-0.0.0-py3-none-any.whl'),
            retriever_type='NullPkgRetriever',
            provider_type='DistCopyProvider'
        ),
        '05': OrigSrcPreparerTestCondition(
            orig_pkg_ref_command='black',
            retriever_type='PyPIPkgRetriever',
            provider_type='NullDistProvider'
        ),
        '06': OrigSrcPreparerTestCondition(
            orig_pkg_ref_command='https://github.com/psf/black',
            retriever_type='GithubPkgRetriever',
            provider_type='WheelAndSdistProvider'
        )
    }

    def build_osp(self,
                  condition_id: str,
                  construction_dir_command: str = None):
        test_condition = self.test_conditions[condition_id]
        orig_src_preparer_builder = sb.OrigSrcPreparerBuilder(
            construction_dir_command=construction_dir_command,
            orig_pkg_ref_command=test_condition.orig_pkg_ref_command)
        return orig_src_preparer_builder.create()

    def run_osp_tests(self, condition_id: str, custom_dir_path: Path):
        test_condition = self.test_conditions[condition_id]

        temp_dir_osp = self.build_osp(condition_id=condition_id)
        assert type(temp_dir_osp._retriever).__name__ ==\
               test_condition.retriever_type
        assert type(temp_dir_osp._provider).__name__ ==\
               test_condition.provider_type
        assert type(temp_dir_osp._receiver).__name__ ==\
               'TempConstructionDir'

        custom_dir_osp = self.build_osp(
            condition_id=condition_id,
            construction_dir_command=str(custom_dir_path))
        assert type(custom_dir_osp._retriever).__name__ == \
               test_condition.retriever_type
        assert type(custom_dir_osp._provider).__name__ == \
               test_condition.provider_type
        assert type(custom_dir_osp._receiver).__name__ == \
               'CustomConstructionDir'

    def test_all_conditions(self, tmp_path):
        for test_condition in self.test_conditions.keys():
            self.run_osp_tests(test_condition, tmp_path)


class TestServiceBuilder:

    local_test_pkgs_path = Path(__file__).parent.absolute() / \
                           'package_test_cases'

    def test_scb_init_dummy_path(self):
        my_command = nds.SrepkgCommand(
            orig_pkg_ref='./dummy_path',
            srepkg_name=None,
            construction_dir=None,
            dist_out_dir=None
        )

        my_service_builder = sb.ServiceBuilder(my_command)
        assert my_service_builder._osp_builder._construction_dir_command is None
        assert my_service_builder._osp_builder._orig_pkg_ref_command ==\
               './dummy_path'

    def test_scb_osp_builder_create_dummy_path(self):
        my_command = nds.SrepkgCommand(
            orig_pkg_ref='./dummy_path',
            srepkg_name=None,
            construction_dir=None,
            dist_out_dir=None
        )
        my_service_builder = sb.ServiceBuilder(my_command)
        with pytest.raises(SystemExit):
            my_service_builder.create_orig_src_preparer()

    def test_scb_osp_builder_create_valid_pkg_ref(self):
        my_command = nds.SrepkgCommand(
            orig_pkg_ref=str(self.local_test_pkgs_path / 'testproj'),
            srepkg_name=None,
            construction_dir=None,
            dist_out_dir=None
        )
        my_service_builder = sb.ServiceBuilder(my_command)
        osp_builder = my_service_builder.create_orig_src_preparer()
        assert type(osp_builder._retriever).__name__ == 'NullPkgRetriever'
        assert type(osp_builder._provider).__name__ == 'WheelAndSdistProvider'
        assert type(osp_builder._receiver).__name__ == 'TempConstructionDir'


# TODO Move tests below this line to test_orig_src_preparer.py

def test_scb_create_src_preparer():
    my_command = nds.SrepkgCommand(
        orig_pkg_ref='/Users/duane/dproj/srepkg/src/srepkg/test/package_test_cases/testproj',
        srepkg_name=None,
        construction_dir=None,
        dist_out_dir=None
    )

    my_service_builder = sb.ServiceBuilder(my_command)
    my_src_preparer = my_service_builder.create_orig_src_preparer()
    my_src_preparer.prepare()


def test_scb_create_src_preparer_custom_dir():
    my_command = nds.SrepkgCommand(
        orig_pkg_ref='/Users/duane/dproj/srepkg/src/srepkg/test/package_test_cases/testproj-0.0.0-py3-none-any.whl',
        srepkg_name=None,
        construction_dir='/Users/duane/dproj/srepkg/src/srepkg/test/package_test_cases/construction_test',
        dist_out_dir=None
    )

    my_service_builder = sb.ServiceBuilder(my_command)
    my_src_preparer = my_service_builder.create_orig_src_preparer()
    my_src_preparer.prepare()
    # my_src_preparer._retriever.retrieve()
    # my_src_preparer._provider.provide()
    # my_src_preparer._receiver.build_missing_items()

    # print('break_for_test')
    # my_src_preparer._receiver.build_missing_items()


def test_src_preparer_prepare():
    my_command = nds.SrepkgCommand(
        orig_pkg_ref='/Users/duane/dproj/srepkg/src/srepkg/test/package_test_cases/testproj',
        srepkg_name=None,
        construction_dir=None,
        dist_out_dir=None
    )

    my_service_builder = sb.ServiceBuilder(my_command)
    my_src_preparer = my_service_builder.create_orig_src_preparer()
    my_src_preparer.prepare()


