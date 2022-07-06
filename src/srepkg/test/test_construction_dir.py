import argparse
import shutil
import unittest
from pathlib import Path

import srepkg.construction_dir as cd


class TestConstructionDir(unittest.TestCase):
    args = argparse.Namespace(
        construction_dir=str(Path(__file__).parent / 'construction_test'))

    def setUp(self) -> None:
        if (Path(__file__).parent / 'construction_test').exists():
            shutil.rmtree(Path(__file__).parent / 'construction_test')
        (Path(__file__).parent / 'construction_test').mkdir()

        self.construction_dir = cd.create_construction_dir(
            self.args.construction_dir)
        print(self.construction_dir._construction_dir.absolute())

    def tearDown(self) -> None:
        if self.construction_dir._construction_dir.exists():
            shutil.rmtree(self.construction_dir._construction_dir)

    def test_temporary_construction_dir_creation(self):
        assert self.construction_dir._construction_dir.exists()
        assert self.construction_dir._srepkg_root.exists()
        assert self.construction_dir._srepkg.exists()
        assert self.construction_dir._srepkg.parent ==\
               self.construction_dir._srepkg_root
        assert self.construction_dir._srepkg_root.parent ==\
               self.construction_dir._construction_dir

    def test_temporary_construction_dir_rename(self):
        self.construction_dir.rename_sub_dirs(
            srepkg_root='new_srepkg_root', srepkg='new_srepkg')
        assert self.construction_dir._srepkg_root.name == 'new_srepkg_root'
        assert self.construction_dir._srepkg.name == 'new_srepkg'
        assert self.construction_dir._srepkg.parent ==\
               self.construction_dir._srepkg_root
        assert self.construction_dir._srepkg_root.parent ==\
               self.construction_dir._construction_dir

    def test_temporary_construction_dir_cleanup(self):
        self.construction_dir.settle()
        assert self.construction_dir._construction_dir.exists()


class TestTemporaryConstructionDir(TestConstructionDir):
    args = argparse.Namespace(construction_dir=None)

    def tearDown(self) -> None:
        self.construction_dir.settle()

    def test_temporary_construction_dir_cleanup(self):
        self.construction_dir.settle()
        assert not self.construction_dir._construction_dir.exists()
