import pytest
from unittest import mock
from packaging.utils import parse_wheel_filename
import srepkg.remote_pkg_retriever as rpr
from test.shared_fixtures import sample_pkgs, tmp_construction_dir


class TestRemotePackageRetriever:

    @pytest.mark.parametrize(
        "pkg_retriever, t_pkg_ref, num_whl_download, num_sdist_download",
        [
            ("PyPIPkgRetriever", "scrape_py_pi", 1, 0),
            # numpy file availability on PyPI inconsistent so remove test
            # depends on Python version and also can be unpredictable when
            # pakage maintainer is updating something
            # ("PyPIPkgRetriever", "numpy_py_pi", 1, 1),
            ("GithubPkgRetriever", "howdoi_github", 0, 0),
        ],
    )
    def test_retriever(
        self,
        pkg_retriever,
        t_pkg_ref,
        num_whl_download,
        num_sdist_download,
        sample_pkgs,
        tmp_construction_dir,
    ):
        retriever_constructor = getattr(rpr, pkg_retriever)
        pkg_ref = getattr(sample_pkgs, t_pkg_ref)

        if pkg_retriever == "GithubPkgRetriever":
            constructor_args = {"pkg_ref": pkg_ref}
        else:
            constructor_args = {
                "pkg_ref": pkg_ref,
                "copy_dest": tmp_construction_dir.orig_pkg_dists,
            }

        retriever_constructor(**constructor_args).run()
        dists_in_cdir = list(tmp_construction_dir.orig_pkg_dists.iterdir())
        num_whl = len(
            [item for item in dists_in_cdir if item.suffix == ".whl"]
        )
        num_sdist = len(
            [item for item in dists_in_cdir if item.suffix == ".gz"]
        )
        assert num_whl == num_whl_download
        assert num_sdist == num_sdist_download


class TestPyPIPkgRetriever:

    def test_custom_version(self, tmp_path):
        retriever = rpr.PyPIPkgRetriever(
            pkg_ref="scrape", copy_dest=tmp_path, version_command="0.11.1"
        )
        retriever.run()
        copy_dest_contents = list(tmp_path.iterdir())
        downloaded_whl = [
            item for item in copy_dest_contents if item.suffix == ".whl"
        ]
        downloaded_whl_filename = downloaded_whl[0].name
        name, version, bld, tag = parse_wheel_filename(downloaded_whl_filename)
        assert str(version) == retriever._version_command

    def test_no_pi_whl_no_sdist(self, tmp_path):
        with mock.patch.object(
            rpr.PyPIPkgRetriever, "_has_sdist", new_callable=mock.PropertyMock
        ) as mock_has_dist:
            mock_has_dist.return_value = False
            retriever = rpr.PyPIPkgRetriever(
                pkg_ref="numpy", copy_dest=tmp_path
            )
            retriever.run()

    def test_only_sdist(self, tmp_path):
        retriever = rpr.PyPIPkgRetriever(pkg_ref="howdoi", copy_dest=tmp_path)
        retriever.run()
