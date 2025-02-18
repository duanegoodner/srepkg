from pathlib import Path
from typing import NamedTuple
from unittest import mock
import srepkg.repackager_interfaces as rep_int
import srepkg.service_builder as sb
import srepkg.srepkg_builder as s_bldr
from test.shared_fixtures import dummy_cdir_summary


class BuilderTestCondition(NamedTuple):
    pkg_ref: str
    srepkg_zip_exists: bool
    srepkg_whl_exists: bool


class TestSrepkgBuilder:
    local_test_pkgs_path = (
        Path(__file__).parent.absolute() / "package_test_cases"
    )

    good_test_conditions = [
        BuilderTestCondition(
            pkg_ref=str(local_test_pkgs_path / "testproj"),
            srepkg_zip_exists=True,
            srepkg_whl_exists=True,
        ),
        # BuilderTestCondition(
        #     pkg_ref=str(
        #         local_test_pkgs_path /
        #         'numpy-1.23.2-cp39-cp39-macosx_10_9_x86_64.whl'),
        #     srepkg_zip_exists=False,
        #     srepkg_whl_exists=True
        # )
    ]

    @staticmethod
    def run_test_condition(
        condition: BuilderTestCondition, dist_out_dir: Path
    ):
        srepkg_command = rep_int.SrepkgCommand(
            orig_pkg_ref=condition.pkg_ref, dist_out_dir=str(dist_out_dir)
        )
        service_builder = sb.ServiceBuilder(srepkg_command=srepkg_command)
        osp = service_builder.create_orig_src_preparer()
        construction_dir_summary = osp.prepare()
        srepkg_builder = service_builder.create_srepkg_builder(
            construction_dir_summary=construction_dir_summary
        )
        srepkg_builder.build()

    def test_good_builder_conditions(self, tmp_path_factory):
        for condition in self.good_test_conditions:
            dist_out_dir = tmp_path_factory.mktemp("dist_out")
            self.run_test_condition(
                condition=condition, dist_out_dir=dist_out_dir
            )
            dist_out_contents = list(dist_out_dir.iterdir())
            dist_out_filetypes = [item.suffix for item in dist_out_contents]
            assert (
                ".gz" in dist_out_filetypes
            ) == condition.srepkg_zip_exists
            assert (
                ".whl" in dist_out_filetypes
            ) == condition.srepkg_whl_exists

    # def mock_build_wheel(self):
    #     pass

    def test_init_builder_without_completers(self, dummy_cdir_summary):
        srepkg_builder = s_bldr.SrepkgBuilder(
            construction_dir_summary=dummy_cdir_summary,
            output_dir=Path("dummy"),
        )

    # No longer using .zip for sdist
    # def test_zip_dir_file_exclusion(
    #     self, tmp_path_factory, dummy_cdir_summary
    # ):
    #     src_path = tmp_path_factory.mktemp("src_path")
    #     (src_path / "file_to_exclude.txt").touch()
    #     dest_dir = tmp_path_factory.mktemp("dest_dir")
    #
    #     zip_name = str(dest_dir / "dest_zip.zip")
    #     s_bldr.SrepkgSdistWriter(
    #         orig_pkg_summary=dummy_cdir_summary, dist_out_dir=dest_dir
    #     ).write_to_zip(
    #         zip_name=zip_name,
    #         # src_path=src_path,
    #         # exclude_paths=[src_path / "file_to_exclude.txt"],
    #     )

    def test_copy_ready_comps_with_dir_as_content(
        self, dummy_cdir_summary, tmp_path_factory
    ):
        srepkg_root = tmp_path_factory.mktemp("srepkg_root")
        cdir_summary = dummy_cdir_summary
        cdir_summary.srepkg_root = srepkg_root

        repackaging_components = tmp_path_factory.mktemp("components_dir")
        (repackaging_components / "wheel_completer_components").mkdir()
        (repackaging_components / "wheel_completer_templates").mkdir()

        dummy_content_path = repackaging_components / "content"
        dummy_content_path.mkdir()

        with mock.patch(
            "srepkg.srepkg_builder.SrepkgWheelCompleter._props",
            new_callable=mock.PropertyMock,
        ) as mock_props:
            mock_props.return_value = s_bldr.CompleterProperties(
                components_dir=repackaging_components,
                templates_dir=Path("dummy"),
                dist_writer_type=s_bldr.SrepkgWheelWriter,
            )

            wheel_completer = s_bldr.SrepkgWheelCompleter(
                orig_pkg_summary=cdir_summary,
                dist_out_dir=Path("dummy"),
                repkg_components=repackaging_components,
            )

            wheel_completer._copy_ready_components()
