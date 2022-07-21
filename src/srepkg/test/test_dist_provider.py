from pathlib import Path

import srepkg.shared_data_structures.new_data_structures as nds


class TestDistProviders:
    local_test_pkgs_path = Path(__file__).parent.absolute() / \
                           'package_test_cases'

    local_src_path = local_test_pkgs_path / 'testproj'
    local_wheel_path = local_test_pkgs_path / 'testproj-0.0.0-py3-none-any.whl'
    local_targz_path = local_wheel_path / 'testproj-0.0.0.tar.gz'
    local_zip_path = local_test_pkgs_path / 'testproj-0.0.0.zip'

    @staticmethod
    def build_command(orig_pkg_path):
        return nds.SrepkgCommand(
            orig_pkg_ref=str(orig_pkg_path),
            srepkg_name=None,
            construction_dir=None,
            dist_out_dir=None
        )

