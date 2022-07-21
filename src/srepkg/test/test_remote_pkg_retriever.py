from pathlib import Path
import srepkg.service_builder as sb
import srepkg.shared_data_structures.new_data_structures as nds


class TestOrigSrcPreparerRetrieverOps:
    local_test_pkgs_path = Path(__file__).parent.absolute() / \
                           'package_test_cases'

    local_src_path = local_test_pkgs_path / 'testproj'
    local_wheel_path = local_test_pkgs_path / 'testproj-0.0.0-py3-none-any.whl'
    local_targz_path = local_wheel_path / 'testproj-0.0.0.tar.gz'
    local_zip_path = local_test_pkgs_path / 'testproj-0.0.0.zip'

    @staticmethod
    def create_src_preparer(
            orig_pkg_ref: str,
            srepkg_name: str = None,
            construction_dir: str = None,
            dist_out_dir: str = None):
        command = nds.SrepkgCommand(
            orig_pkg_ref=orig_pkg_ref,
            srepkg_name=srepkg_name,
            construction_dir=construction_dir,
            dist_out_dir=dist_out_dir)

        src_preparer = sb.ServiceBuilder(command).create_orig_src_preparer()



