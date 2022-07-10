import abc
import tempfile
import uuid
from pathlib import Path
import srepkg.shared_interfaces as shared_int
import srepkg.repackager_new_interfaces as re_int


class GenConstructionDir(re_int.RenamableSrepkgDirInterface,
                         shared_int.WritableSrepkgDirInterface):
    @abc.abstractmethod
    def __init__(self, construction_dir: Path):
        self._construction_dir = construction_dir
        self._srepkg_root = construction_dir / uuid.uuid4().hex
        self._srepkg_root.mkdir()
        self._srepkg = self._srepkg_root / uuid.uuid4().hex
        self._srepkg.mkdir()

    @property
    def srepkg_path(self):
        return self._srepkg

    def rename_sub_dirs(self, srepkg_root: str, srepkg: str):
        self._srepkg.rename(self._srepkg.parent.absolute() / srepkg)
        self._srepkg_root.rename(self._srepkg_root.parent.absolute()
                                 / srepkg_root)
        self._srepkg_root = self._srepkg_root.parent.absolute() / srepkg_root
        self._srepkg = self._srepkg_root / srepkg

    # TODO Implement either here or in each subclasses (probably here)
    def build_missing_items(self):
        pass


class CustomConstructionDir(GenConstructionDir):
    def __init__(self, construction_dir: Path):
        super().__init__(construction_dir)

    def settle(self):
        print(f"An uncompressed copy of {self._srepkg.name} has been saved in "
              f"{str(self._srepkg_root)}")


class TempConstructionDir(GenConstructionDir):
    def __init__(self):
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        super().__init__(Path(self._temp_dir_obj.name))

    def settle(self):
        self._temp_dir_obj.cleanup()
