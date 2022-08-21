import pytest
import srepkg.service_builder as sb
from pathlib import Path
from typing import NamedTuple
import srepkg.repackager_interfaces as rep_int
from srepkg.service_registry import ServiceRegistry


class TestConstructionDirDispatch:

    def test_none_create_arg(self):
        construction_dir = sb.create_construction_dir(None)
        assert type(construction_dir).__name__ == 'TempConstructionDir'

    def test_string_create_arg(self, tmp_path):
        construction_dir = sb.create_construction_dir(str(tmp_path))
        assert type(construction_dir).__name__ == 'CustomConstructionDir'

    def test_path_create_arg(self, tmp_path):
        construction_dir = sb.create_construction_dir(tmp_path)
        assert type(construction_dir).__name__ == 'CustomConstructionDir'

    def test_invalid_construction_dir_arg(self):
        with pytest.raises(NotImplementedError):
            construction_dir = sb.create_construction_dir(1)



class RetrieverProviderTestCondition(NamedTuple):
    pkg_ref_command: str
    retriever_type: str
    provider_type: str


class OSPRetrieverProviderTester:
    construction_dir = sb.create_construction_dir(None)
    package_test_cases = Path(__file__).parent.absolute() / 'package_test_cases'

    @property
    def test_conditions(self):
        return {
            1: RetrieverProviderTestCondition(
                pkg_ref_command=str(self.package_test_cases / 'testproj'),
                retriever_type='NullPkgRetriever',
                provider_type='DistProviderFromSrc'
            ),
            2: RetrieverProviderTestCondition(
                pkg_ref_command=str(
                    self.package_test_cases / 'testproj-0.0.0.tar.gz'),
                retriever_type='NullPkgRetriever',
                provider_type='DistCopyProvider'),
            3: RetrieverProviderTestCondition(
                pkg_ref_command=str(
                    self.package_test_cases / 'testproj-0.0.0.zip'),
                retriever_type='NullPkgRetriever',
                provider_type='DistCopyProvider'),
            4: RetrieverProviderTestCondition(
                pkg_ref_command=str(
                    self.package_test_cases / 'testproj-0.0.0-py3-none-any.whl'),
                retriever_type='NullPkgRetriever',
                provider_type='DistCopyProvider'),
            5: RetrieverProviderTestCondition(
                pkg_ref_command='black',
                retriever_type='PyPIPkgRetriever',
                provider_type='NullDistProvider'),
            6: RetrieverProviderTestCondition(
                pkg_ref_command='https://github.com/psf/black',
                retriever_type='GithubPkgRetriever',
                provider_type='DistProviderFromSrc')
        }


class TestRetrieverProviderDispatch(OSPRetrieverProviderTester):

    def run_test_condition(
            self,
            test_condition: RetrieverProviderTestCondition):
        pkg_retriever = sb.PkgRetrieverDispatch(
            test_condition.pkg_ref_command).create(self.construction_dir)
        dist_provider = sb.DistProviderDispatch(
            test_condition.pkg_ref_command).create(self.construction_dir)

        assert type(pkg_retriever).__name__ == test_condition.retriever_type
        assert type(dist_provider).__name__ == test_condition.provider_type

    def test_retriever_provider_conditions(self):
        for condition in self.test_conditions:
            self.run_test_condition(self.test_conditions[condition])


class OrigSrcPreparerTestCondition(NamedTuple):
    pkg_ref_command: str
    retriever_type: str
    provider_type: str


class TestOSPBuilder(OSPRetrieverProviderTester):
    service_registry = ServiceRegistry()

    def build_osp(self,
                  condition_id: int,
                  construction_dir_command: str = None):
        test_condition = self.test_conditions[condition_id]
        orig_src_preparer_builder = sb.OrigSrcPreparerBuilder(
            construction_dir_command=construction_dir_command,
            orig_pkg_ref_command=test_condition.pkg_ref_command,
            service_registry=self.service_registry)
        return orig_src_preparer_builder.create()

    def run_osp_test(self, condition_id: int):
        test_condition = self.test_conditions[condition_id]

        temp_dir_osp = self.build_osp(condition_id=condition_id)
        assert type(temp_dir_osp._retriever).__name__ == \
               test_condition.retriever_type
        assert type(temp_dir_osp._provider).__name__ == \
               test_condition.provider_type
        assert type(temp_dir_osp._receiver).__name__ == \
               'TempConstructionDir'
        self.service_registry.reset()

    def test_osp_conditions(self):
        for condition_id in self.test_conditions:
            self.run_osp_test(condition_id=condition_id)


class TestServiceBuilderCreateOSP(OSPRetrieverProviderTester):

    def run_create_osp_test(self, condition_id: int):
        test_condition = self.test_conditions[condition_id]
        srepkg_command = rep_int.SrepkgCommand(
            orig_pkg_ref=test_condition.pkg_ref_command)

        service_builder = sb.ServiceBuilder(srepkg_command=srepkg_command)
        osp = service_builder.create_orig_src_preparer()
        assert type(osp._retriever).__name__ == \
               test_condition.retriever_type
        assert type(osp._provider).__name__ == \
               test_condition.provider_type
        assert type(osp._receiver).__name__ == \
               'TempConstructionDir'

    def test_osp_creation_conditions(self):
        for condition_id in self.test_conditions:
            self.run_create_osp_test(condition_id=condition_id)


class BuilderDispatchCondition(NamedTuple):
    pkg_ref: str
    sdist_completer_exists: bool
    wheel_completer_exists: bool


class TestSrepkgBuilderDispatch:
    local_test_pkgs_path = Path(__file__).parent.absolute() / \
                           'package_test_cases'

    test_conditions = [
        BuilderDispatchCondition(
            pkg_ref=str(local_test_pkgs_path / 'testproj'),
            sdist_completer_exists=True,
            wheel_completer_exists=True),
        # BuilderDispatchCondition(
        #     pkg_ref=str(
        #         local_test_pkgs_path /
        #         'numpy-1.23.2-cp39-cp39-macosx_10_9_x86_64.whl'),
        #     sdist_completer_exists=False,
        #     wheel_completer_exists=True
        # ),
        BuilderDispatchCondition(
            pkg_ref=str(local_test_pkgs_path /
                        'testproj-0.0.0-py3-none-any.whl'),
            sdist_completer_exists=True,
            wheel_completer_exists=True
        )
    ]

    @staticmethod
    def run_test_condition(condition: BuilderDispatchCondition):
        srepkg_command = rep_int.SrepkgCommand(orig_pkg_ref=condition.pkg_ref)
        service_builder = sb.ServiceBuilder(srepkg_command=srepkg_command)
        osp = service_builder.create_orig_src_preparer()
        osp.prepare()
        srepkg_builder = service_builder.create_srepkg_builder()
        return srepkg_builder

    def test_dispatch_conditions(self):
        for condition in self.test_conditions:
            srepkg_builder = self.run_test_condition(condition)
            completer_types = [type(item).__name__ for item in
                               srepkg_builder._srepkg_completers]
            assert ('SrepkgSdistCompleter' in completer_types) ==\
                   condition.sdist_completer_exists
            assert ('SrepkgWheelCompleter' in completer_types) ==\
                   condition.wheel_completer_exists
