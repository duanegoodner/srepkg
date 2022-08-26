import pytest
import srepkg.service_builder as sb
from typing import NamedTuple
import srepkg.repackager_interfaces as rep_int
from srepkg.test.shared_fixtures import tmp_construction_dir, sample_pkgs


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


osp_conditions = [
    ("testproj", "NullPkgRetriever", "DistProviderFromSrc"),
    ("testproj_targz", "NullPkgRetriever", "DistCopyProvider"),
    ("testproj_zip", "NullPkgRetriever", "DistCopyProvider"),
    ("black_py_pi", "PyPIPkgRetriever", "NullDistProvider"),
    ("black_github", "GithubPkgRetriever", "DistProviderFromSrc")
]


class TestRetrieverProviderDispatch:

    @pytest.mark.parametrize("pkg_ref_attr, retriever_type, provider_type",
                             osp_conditions)
    def test_conditions(self, pkg_ref_attr, retriever_type, provider_type,
                        tmp_construction_dir, sample_pkgs):
        pkg_ref_command = getattr(sample_pkgs, pkg_ref_attr)
        pkg_retriever = sb.PkgRetrieverDispatch(
            pkg_ref_command=pkg_ref_command,
            construction_dir=tmp_construction_dir).create()
        dist_provider = sb.DistProviderDispatch(
            pkg_ref_command=pkg_ref_command,
            construction_dir=tmp_construction_dir,
            retriever=pkg_retriever).create()

        assert type(pkg_retriever).__name__ == retriever_type
        assert type(dist_provider).__name__ == provider_type


class TestOSPBuilder:

    @pytest.mark.parametrize("pkg_ref_attr, retriever_type, provider_type",
                             osp_conditions)
    def test_osp_condition(self, pkg_ref_attr, retriever_type, provider_type,
                           sample_pkgs):
        orig_pkg_ref_command = getattr(sample_pkgs, pkg_ref_attr)
        osp_builder = sb.OrigSrcPreparerBuilder(
            orig_pkg_ref_command=orig_pkg_ref_command,
            construction_dir_command=None)
        osp = osp_builder.create()
        assert type(osp._retriever).__name__ == retriever_type
        assert type(osp._provider).__name__ == provider_type
        assert type(osp._receiver).__name__ == "TempConstructionDir"


class TestServiceBuilderCreateOSP:

    @pytest.mark.parametrize("pkg_ref_attr, retriever_type, provider_type",
                             osp_conditions)
    def test_create_osp(self, pkg_ref_attr, retriever_type, provider_type,
                        sample_pkgs):
        srepkg_command = rep_int.SrepkgCommand(
            orig_pkg_ref=getattr(sample_pkgs, pkg_ref_attr))
        service_builder = sb.ServiceBuilder(srepkg_command=srepkg_command)
        osp = service_builder.create_orig_src_preparer()
        assert type(osp._retriever).__name__ == retriever_type
        assert type(osp._provider).__name__ == provider_type
        assert type(osp._receiver).__name__ == "TempConstructionDir"


bldr_dispatch_conditions = [
    ("testproj", True, True),
    ("numpy_whl", False, True),
    ("testproj_whl", True, True)
]


class TestBuilderDispatch:

    @pytest.mark.parametrize(
        "pkg_ref_attr, sdist_completer_exists, wheel_completer_exists",
        bldr_dispatch_conditions)
    def test_bldr_dispatch_conditions(self, pkg_ref_attr, sdist_completer_exists,
                                      wheel_completer_exists, sample_pkgs):
        srepkg_command = rep_int.SrepkgCommand(
            orig_pkg_ref=getattr(sample_pkgs, pkg_ref_attr))
        service_builder = sb.ServiceBuilder(srepkg_command)
        osp = service_builder.create_orig_src_preparer()
        orig_src_summary = osp.prepare()
        srepkg_builder = service_builder.create_srepkg_builder(
            construction_dir_summary=orig_src_summary)
        completer_types = [type(item).__name__ for item in
                           srepkg_builder._srepkg_completers]

        assert ('SrepkgSdistCompleter' in completer_types) == \
               sdist_completer_exists
        assert ('SrepkgWheelCompleter' in completer_types) == \
               wheel_completer_exists
