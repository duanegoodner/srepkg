import pytest
import unittest.mock as mock
import srepkg.error_handling.custom_exceptions as ce
import srepkg.service_builder
import srepkg.srepkg_builder as sbn
import srepkg.service_builder as sb
import srepkg.repackager_interfaces as rep_int
from test.shared_fixtures import (
    tmp_construction_dir,
    sample_pkgs,
    dummy_cdir_summary,
)


class TestConstructionDirDispatch:

    def test_none_create_arg(self):
        construction_dir = sb.create_construction_dir(None)
        assert type(construction_dir).__name__ == "TempConstructionDir"

    def test_string_create_arg(self, tmp_path):
        construction_dir = sb.create_construction_dir(str(tmp_path))
        assert type(construction_dir).__name__ == "CustomConstructionDir"

    def test_path_create_arg(self, tmp_path):
        construction_dir = sb.create_construction_dir(tmp_path)
        assert type(construction_dir).__name__ == "CustomConstructionDir"

    def test_invalid_construction_dir_arg(self):
        with pytest.raises(NotImplementedError):
            construction_dir = sb.create_construction_dir(1)


class TestRetrieverProviderDispatch:
    osp_conditions = [
        ("testproj", ["DistProviderFromSrc"]),
        ("testproj_targz", ["DistCopyProvider"]),
        ("testproj_zip", ["DistCopyProvider"]),
        ("black_py_pi", ["PyPIPkgRetriever"]),
        ("black_github", ["GithubPkgRetriever", "DistProviderFromSrc"]),
    ]

    @pytest.mark.parametrize(
        "pkg_ref_attr, retriever_provider_components", osp_conditions
    )
    def test_conditions(
        self,
        pkg_ref_attr,
        retriever_provider_components,
        tmp_construction_dir,
        sample_pkgs,
    ):
        pkg_ref_command = getattr(sample_pkgs, pkg_ref_attr)
        retriever_provider = sb.RetrieverProviderDispatch(
            pkg_ref_command=pkg_ref_command,
            construction_dir=tmp_construction_dir,
        ).create()
        assert [
            (type(item).__name__ for item in retriever_provider)
            == retriever_provider_components
        ]

    def test_github_commit_arg_with_non_repo_source(
        self, tmp_construction_dir, sample_pkgs
    ):

        with pytest.raises(ce.UnusableGitCommitRef):
            retriever_provider = sb.RetrieverProviderDispatch(
                pkg_ref_command=sample_pkgs.testproj,
                construction_dir=tmp_construction_dir,
                git_ref="dummy_git_ref",
            ).create()

    def test_version_arg_for_non_pypi_pkg_ref(
        self, tmp_construction_dir, sample_pkgs
    ):

        with pytest.raises(ce.UnusableVersionArgument):
            retriever_provider = sb.RetrieverProviderDispatch(
                pkg_ref_command=sample_pkgs.testproj,
                construction_dir=tmp_construction_dir,
                version_command="1.0.0",
            ).create()


class TestSrepkgBuilderBuilder:

    def test_no_completer_sources(self, dummy_cdir_summary):
        with mock.patch(
            "srepkg.service_builder.SrepkgBuilderBuilder."
            "_completer_dispatch",
            new_callable=mock.PropertyMock,
        ) as mock_completer_dispatch:
            mock_completer_dispatch.return_value = {
                sbn.SrepkgWheelCompleter: None,
                sbn.SrepkgSdistCompleter: None,
            }
            srepkg_builder = sb.SrepkgBuilderBuilder(
                output_dir_command=None,
                construction_dir_summary=dummy_cdir_summary,
            ).create()

        mock_completer_dispatch.assert_called_once_with()


service_bldr_conditions = [
    "testproj",
    # "numpy_whl",
    # "testproj_whl"
]


class TestServiceBuilder:

    @pytest.mark.parametrize("pkg_ref_attr", service_bldr_conditions)
    @mock.patch.object(srepkg.service_builder.OrigSrcPreparerBuilder, "create")
    def test_create_osp(self, mock_create, pkg_ref_attr, sample_pkgs):
        srepkg_command = rep_int.SrepkgCommand(
            orig_pkg_ref=getattr(sample_pkgs, pkg_ref_attr)
        )
        service_builder = sb.ServiceBuilder(srepkg_command)
        osp = service_builder.create_orig_src_preparer()
        mock_create.assert_called_with()

    @pytest.mark.parametrize("pkg_ref_attr", service_bldr_conditions)
    @mock.patch("srepkg.srepkg_builder.SrepkgWheelCompleter")
    @mock.patch("srepkg.srepkg_builder.SrepkgSdistCompleter")
    def test_create_srepkg_builder(
        self,
        MockSrepkgWheelComleter,
        MockSrepkgSdistCompleter,
        pkg_ref_attr,
        sample_pkgs,
    ):
        srepkg_command = rep_int.SrepkgCommand(
            orig_pkg_ref=getattr(sample_pkgs, pkg_ref_attr)
        )
        service_builder = sb.ServiceBuilder(srepkg_command)
        osp = service_builder.create_orig_src_preparer()
        orig_src_summary = osp.prepare()
        srepkg_builder = service_builder.create_srepkg_builder(
            orig_src_summary
        )
        assert MockSrepkgWheelComleter.called
        assert MockSrepkgSdistCompleter.called
