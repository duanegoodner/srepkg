from argparse import Namespace
import srepkg.shared_data_structures.new_data_structures as nds
import srepkg.service_builder as sb


def test_scb_init():
    my_command = nds.SrepkgCommand(
        orig_pkg_ref='./dummy_path',
        srepkg_name=None,
        construction_dir=None,
        dist_out_dir=None
    )

    my_service_builder = sb.ServiceBuilder(my_command)


def test_scb_create_src_preparer():
    my_command = nds.SrepkgCommand(
        orig_pkg_ref='/Users/duane/dproj/srepkg/src/srepkg/test/package_test_cases/testproj',
        srepkg_name=None,
        construction_dir=None,
        dist_out_dir=None
    )

    my_service_builder = sb.ServiceBuilder(my_command)
    my_src_preparer = my_service_builder.create_orig_src_preparer()


def test_pkg_type_identifier_pypi_black():
    assert sb.PkgTypeIdentifier("black")._is_pypi_pkg()


def test_pkg_type_identifier_testproj():
    my_identifier = sb.PkgTypeIdentifier(
        '/Users/duane/dproj/srepkg/src/srepkg/test/package_test_cases/testproj'
    )
    assert my_identifier.get_potential_pkg_type() == sb.PkgRefType.LOCAL_SRC
