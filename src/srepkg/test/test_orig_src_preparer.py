import pytest
from pathlib import Path
import srepkg.service_builder as sb
import srepkg.shared_data_structures.new_data_structures as nds


class TestOrigSrcPreparer:
    local_test_pkgs_path = Path(__file__).parent.absolute() / \
                           'package_test_cases'

    def test_local_src(self):
        my_command = nds.SrepkgCommand(
            orig_pkg_ref=str(self.local_test_pkgs_path / 'testproj'),
            srepkg_name=None,
            construction_dir=None,
            dist_out_dir=None
        )

        service_builder = sb.ServiceBuilder(my_command)
        orig_src_preparer = service_builder.create_orig_src_preparer()
        orig_src_preparer.prepare()

        assert orig_src_preparer._receiver.srepkg_inner.exists()

    def test_local_wheel(self):
        my_command = nds.SrepkgCommand(
            orig_pkg_ref=str(self.local_test_pkgs_path /
                             'testproj-0.0.0-py3-none-any.whl'),
            srepkg_name=None,
            construction_dir=self.local_test_pkgs_path / 'construction_test',
            dist_out_dir=None
        )

        service_builder = sb.ServiceBuilder(my_command)
        orig_src_preparer = service_builder.create_orig_src_preparer()
        orig_src_preparer.prepare()
