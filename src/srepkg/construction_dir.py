import abc
import tempfile
import uuid
from functools import singledispatchmethod
from pathlib import Path


class ConstructionDirInterface(abc.ABC):
    def __init__(self, construction_dir: Path):
        self._construction_dir = construction_dir
        self._srepkg_root = construction_dir / uuid.uuid4().hex
        self._srepkg_root.mkdir()
        self._srepkg = self._srepkg_root / uuid.uuid4().hex
        self._srepkg.mkdir()

    def rename_sub_dirs(self, srepkg_root: str, srepkg: str):
        self._srepkg.rename(self._srepkg.parent.absolute() / srepkg)
        self._srepkg_root.rename(self._srepkg_root.parent.absolute()
                                 / srepkg_root)

        self._srepkg_root = self._srepkg_root.parent.absolute() / srepkg_root
        self._srepkg = self._srepkg_root / srepkg

    @abc.abstractmethod
    def settle(self):
        pass


class _CustomConstructionDir(ConstructionDirInterface):
    def __init__(self, construction_dir: Path):
        super().__init__(construction_dir)

    def settle(self):
        print(f"An uncompressed copy of {self._srepkg.name} has been saved in "
              f"{str(self._srepkg_root)}")


class _TemporaryConstructionDir(ConstructionDirInterface):
    def __init__(self):
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        super().__init__(Path(self._temp_dir_obj.name))

    def settle(self):
        self._temp_dir_obj.cleanup()


class ConstructionDirBuilder:

    def __init__(self):
        pass

    @singledispatchmethod
    def create(self, arg):
        raise NotImplementedError

    @create.register
    def _(self, arg: None):
        return _TemporaryConstructionDir()

    @create.register
    def _(self, arg: str):
        return _CustomConstructionDir(Path(arg))

    @create.register
    def _(self, arg: Path):
        return _CustomConstructionDir(arg)
