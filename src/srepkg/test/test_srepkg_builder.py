from pathlib import Path
from typing import NamedTuple
import srepkg.repackager_interfaces as rep_int
import srepkg.repackager_data_structs as rep_ds
import srepkg.service_builder as sb
import srepkg.srepkg_builder as s_bldr


class BuilderTestCondition(NamedTuple):
    pkg_ref: str
    srepkg_zip_exists: bool
    srepkg_whl_exists: bool


class TestSrepkgBuilder:
    local_test_pkgs_path = Path(__file__).parent.absolute() / \
                           'package_test_cases'

    good_test_conditions = [
        BuilderTestCondition(
            pkg_ref=str(local_test_pkgs_path / 'testproj'),
            srepkg_zip_exists=True,
            srepkg_whl_exists=True),
        # BuilderTestCondition(
        #     pkg_ref=str(
        #         local_test_pkgs_path /
        #         'numpy-1.23.2-cp39-cp39-macosx_10_9_x86_64.whl'),
        #     srepkg_zip_exists=False,
        #     srepkg_whl_exists=True
        # )
    ]

    @staticmethod
    def run_test_condition(condition: BuilderTestCondition,
                           dist_out_dir: Path):
        srepkg_command = rep_int.SrepkgCommand(
            orig_pkg_ref=condition.pkg_ref,
            dist_out_dir=str(dist_out_dir))
        service_builder = sb.ServiceBuilder(srepkg_command=srepkg_command)
        osp = service_builder.create_orig_src_preparer()
        orig_pkg_src_summary = osp.prepare()
        srepkg_builder = service_builder.create_srepkg_builder(
            orig_pkg_src_summary=orig_pkg_src_summary
        )
        srepkg_builder.build()

    def test_good_builder_conditions(self, tmp_path_factory):
        for condition in self.good_test_conditions:
            dist_out_dir = tmp_path_factory.mktemp("dist_out")
            self.run_test_condition(
                condition=condition,
                dist_out_dir=dist_out_dir)
            dist_out_contents = list(dist_out_dir.iterdir())
            dist_out_filetypes = [item.suffix for item in dist_out_contents]
            assert ('.zip' in dist_out_filetypes) == \
                   condition.srepkg_zip_exists
            assert ('.whl' in dist_out_filetypes) == \
                   condition.srepkg_whl_exists

    def mock_build_wheel(self):
        pass

    # @mock.patch("srepkg.construction_dir.ConstructionDir.has_sdist", new_callable=mock.PropertyMock)
    # @mock.patch("srepkg.construction_dir.SdistToWheelConverter.build_wheel", new=mock_build_wheel)
    # def test_init_builder_without_completers(self, mock_has_sdist):
    #     mock_has_sdist.return_value = True
    #
    #     # with mock.patch.object(
    #     #         cdn.ConstructionDir, "has_sdist",
    #     #         new_callable=mock.PropertyMock) as mock_has_sdist:
    #     #     mock_has_sdist.return_value = True
    #
    #     construction_dir = srepkg.construction_dir.TempConstructionDir()
    #     orig_pkg_src_summary = construction_dir.finalize()
    #     output_dir = Path.cwd()
    #     return s_bldr.SrepkgBuilder(
    #         construction_dir=construction_dir,
    #         orig_pkg_src_summary=orig_pkg_src_summary,
    #         output_dir=output_dir)

    def test_init_builder_without_completers(self):
        srepkg_builder = s_bldr.SrepkgBuilder(
            orig_pkg_src_summary=rep_ds.OrigPkgSrcSummary(
                pkg_name="dummy", pkg_version="dummy", srepkg_name="dummy",
                srepkg_root=Path("dummy"), orig_pkg_dists=Path("dummy"),
                srepkg_inner=Path("dummy")),
            output_dir=Path("dummy")
        )

    def test_zip_dir_file_exclusion(self, tmp_path_factory):
        src_path = tmp_path_factory.mktemp("src_path")
        (src_path / "file_to_exclude.txt").touch()
        dest_dir = tmp_path_factory.mktemp("dest_dir")

        zip_name = str(dest_dir / "dest_zip.zip")
        s_bldr.SrepkgSdistCompleter.zip_dir(
            zip_name=zip_name, src_path=src_path,
            exclude_paths=[src_path / "file_to_exclude.txt"])
