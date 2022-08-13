from pathlib import Path
import srepkg.service_builder as sb
import srepkg.shared_data_structures.new_data_structures as nds
from srepkg.service_registry import SERVICE_REGISTRY


def test_quickly():

    SERVICE_REGISTRY.reset()

    output_dir = Path('/Users/duane/srepkg_pkgs')

    local_test_pkgs_path = Path(__file__).parent.absolute() / \
        'package_test_cases'

    src_code = local_test_pkgs_path / 'testproj-0.0.0.tar.gz'

    cur_command = nds.SrepkgCommand(
        orig_pkg_ref=str(src_code),
        construction_dir=str(output_dir)
    )

    service_builder = sb.ServiceBuilder(cur_command)
    src_preparer = service_builder.create_orig_src_preparer()
    src_preparer.prepare()

    srepkg_builder = service_builder.create_srepkg_builder()
    srepkg_builder.build()

