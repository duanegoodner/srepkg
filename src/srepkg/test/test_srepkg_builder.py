from pathlib import Path
from typing import NamedTuple
import srepkg.repackager_interfaces as rep_int
import srepkg.service_builder as sb


class BuilderTestCondition(NamedTuple):
    pkg_ref: str
    srepkg_zip_exists: bool
    srepkg_whl_exists: bool


class TestSrepkgBuilder:

    local_test_pkgs_path = Path(__file__).parent.absolute() / \
                           'package_test_cases'

    test_conditions = [
        BuilderTestCondition(
            pkg_ref=str(local_test_pkgs_path / 'testproj'),
            srepkg_zip_exists=True,
            srepkg_whl_exists=True),
        BuilderTestCondition(
            pkg_ref=str(
                local_test_pkgs_path /
                'numpy-1.23.2-cp39-cp39-macosx_10_9_x86_64.whl'),
            srepkg_zip_exists=False,
            srepkg_whl_exists=True
        )
    ]

    @staticmethod
    def run_test_condition(condition: BuilderTestCondition,
                           dist_out_dir: Path):
        srepkg_command = rep_int.SrepkgCommand(
            orig_pkg_ref=condition.pkg_ref,
            dist_out_dir=str(dist_out_dir))
        service_builder = sb.ServiceBuilder(srepkg_command=srepkg_command)
        osp = service_builder.create_orig_src_preparer()
        osp.prepare()
        srepkg_builder = service_builder.create_srepkg_builder()
        srepkg_builder.build()

    def test_builder_condition(self, tmp_path_factory):
        for condition in self.test_conditions:
            dist_out_dir = tmp_path_factory.mktemp("dist_out")
            self.run_test_condition(
                condition=condition,
                dist_out_dir=dist_out_dir)
            dist_out_contents = list(dist_out_dir.iterdir())
            dist_out_filetypes = [item.suffix for item in dist_out_contents]
            assert ('.zip' in dist_out_filetypes) ==\
                   condition.srepkg_zip_exists
            assert ('.whl' in dist_out_filetypes) ==\
                   condition.srepkg_whl_exists


# def test_quickly(tmp_path):
#
#     output_dir = tmp_path
#
#     local_test_pkgs_path = Path(__file__).parent.absolute() / \
#         'package_test_cases'
#
#     src_code = local_test_pkgs_path / 'testproj-0.0.0.tar.gz'
#
#     cur_command = rep_int.SrepkgCommand(
#         orig_pkg_ref=str(src_code),
#         construction_dir=str(output_dir)
#     )
#
#     service_builder = sb.ServiceBuilder(cur_command)
#     src_preparer = service_builder.create_orig_src_preparer()
#     src_preparer.prepare()
#
#     srepkg_builder = service_builder.create_srepkg_builder()
#     srepkg_builder.build()

