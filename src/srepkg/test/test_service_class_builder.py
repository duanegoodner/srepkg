from argparse import Namespace
import srepkg.shared_data_structures.new_data_structures as nds
import srepkg.service_builder as sb
from pathlib import Path
import pytest

import srepkg.construction_dir_new as cdn


class TestConstructionDirDispatch:

    dispatch = sb.ConstructionDirDispatch()

    def test_none_create_arg(self):
        construction_dir = self.dispatch.create(None)
        assert type(construction_dir).__name__ == 'TempConstructionDir'

    def test_string_create_arg(self, tmp_path):
        construction_dir = self.dispatch.create(str(tmp_path))
        assert type(construction_dir).__name__ == 'CustomConstructionDir'

    def test_path_create_arg(self, tmp_path):
        construction_dir = self.dispatch.create(tmp_path)
        assert type(construction_dir).__name__ == 'CustomConstructionDir'







def test_path(tmp_path):
    construction_dir_dispatch = sb.ConstructionDirDispatch()
    construction_dir_dispatch.create(tmp_path)


def test_construction_dir_dispatch():
    construction_dir_dispatch = sb.ConstructionDirDispatch()

    temp_construction_dir = construction_dir_dispatch.create(None)
    assert type(temp_construction_dir).__name__ == 'TempConstructionDir'



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
    my_src_preparer.prepare()


def test_scb_create_src_preparer_custom_dir():
    my_command = nds.SrepkgCommand(
        orig_pkg_ref='/Users/duane/dproj/srepkg/src/srepkg/test/package_test_cases/testproj-0.0.0-py3-none-any.whl',
        srepkg_name=None,
        construction_dir='/Users/duane/dproj/srepkg/src/srepkg/test/construction_test',
        dist_out_dir=None
    )

    my_service_builder = sb.ServiceBuilder(my_command)
    my_src_preparer = my_service_builder.create_orig_src_preparer()
    my_src_preparer.prepare()
    # my_src_preparer._retriever.retrieve()
    # my_src_preparer._provider.provide()
    # my_src_preparer._receiver.build_missing_items()

    # print('break_for_test')
    # my_src_preparer._receiver.build_missing_items()


def test_src_preparer_prepare():
    my_command = nds.SrepkgCommand(
        orig_pkg_ref='/Users/duane/dproj/srepkg/src/srepkg/test/package_test_cases/testproj',
        srepkg_name=None,
        construction_dir=None,
        dist_out_dir=None
    )

    my_service_builder = sb.ServiceBuilder(my_command)
    my_src_preparer = my_service_builder.create_orig_src_preparer()
    my_src_preparer.prepare()


def test_pkg_type_identifier_pypi_black():
    assert sb.PkgRefIdentifier("black").is_pypi_pkg()


def test_pkg_type_identifier_testproj():
    my_identifier = sb.PkgRefIdentifier(
        '/Users/duane/dproj/srepkg/src/srepkg/test/package_test_cases/testproj'
    )
    assert my_identifier.identify_specific_type() == sb.PkgRefType.LOCAL_SRC
