import pytest
import unittest.mock as mock

import srepkg.service_builder
import srepkg.service_builder as sb
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


class TestRetrieverProviderDispatch:
    osp_conditions = [
        ("testproj", "NullPkgRetriever", "DistProviderFromSrc"),
        ("testproj_targz", "NullPkgRetriever", "DistCopyProvider"),
        ("testproj_zip", "NullPkgRetriever", "DistCopyProvider"),
        ("black_py_pi", "PyPIPkgRetriever", "NullDistProvider"),
        ("black_github", "GithubPkgRetriever", "DistProviderFromSrc")
    ]

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


# bldr_dispatch_conditions = [
#     ("testproj", True, True),
#     ("numpy_whl", False, True),
#     ("testproj_whl", True, True)
# ]


class TestCompleterDispatches:

    completer_conditions = [
        ("testproj", True, True),
        ("numpy_whl", False, True),
        ("testproj_whl", True, True)
    ]

    @pytest.mark.parametrize(
        "pkg_ref_attr, sdist_completer_exists, wheel_completer_exists",
        completer_conditions)
    def test_sdist_completer_dispatch(
            self, pkg_ref_attr, sdist_completer_exists, wheel_completer_exists, sample_pkgs):
        srepkg_command = rep_int.SrepkgCommand(
            orig_pkg_ref=getattr(sample_pkgs, pkg_ref_attr))
        service_builder = sb.ServiceBuilder(srepkg_command)
        osp = service_builder.create_orig_src_preparer()
        orig_src_summary = osp.prepare()
        sdist_completer_dispatch = sb.SdistCompleterDispatch(
            construction_dir_summary=orig_src_summary)
        sdist_completer = sdist_completer_dispatch.create()
        wheel_completer_dispatch = sb.WheelCompleterDispatch(
            construction_dir_summary=orig_src_summary)
        wheel_completer = wheel_completer_dispatch.create()

        assert (sdist_completer is not None) == sdist_completer_exists
        assert (wheel_completer is not None) == wheel_completer_exists


service_bldr_conditions = [
        "testproj",
        # "numpy_whl",
        # "testproj_whl"
    ]


class TestServiceBuilder:

    @pytest.mark.parametrize(
        "pkg_ref_attr",
        service_bldr_conditions)
    @mock.patch.object(srepkg.service_builder.OrigSrcPreparerBuilder, "create")
    def test_create_osp(self, mock_create, pkg_ref_attr, sample_pkgs):
        srepkg_command = rep_int.SrepkgCommand(
            orig_pkg_ref=getattr(sample_pkgs, pkg_ref_attr))
        service_builder = sb.ServiceBuilder(srepkg_command)
        osp = service_builder.create_orig_src_preparer()
        mock_create.assert_called_with()

    @pytest.mark.parametrize(
        "pkg_ref_attr",
        service_bldr_conditions)
    # @mock.patch.object(srepkg.service_builder.SrepkgBuilderBuilder, "create")
    @mock.patch.object(srepkg.service_builder.SdistCompleterDispatch, "create")
    @mock.patch.object(srepkg.service_builder.WheelCompleterDispatch, "create")
    def test_create_srepkg_builder(
            self, mock_sdist_completer_create, mock_wheel_completer_create,
            pkg_ref_attr, sample_pkgs):
        srepkg_command = rep_int.SrepkgCommand(
            orig_pkg_ref=getattr(sample_pkgs, pkg_ref_attr))
        service_builder = sb.ServiceBuilder(srepkg_command)
        osp = service_builder.create_orig_src_preparer()
        orig_src_summary = osp.prepare()
        srepkg_builder = service_builder.create_srepkg_builder(orig_src_summary)
        mock_sdist_completer_create.assert_called_with()
        mock_wheel_completer_create.assert_called_with()
