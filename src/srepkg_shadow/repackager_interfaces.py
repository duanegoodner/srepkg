import abc
import uuid
from pathlib import Path
import shared_data_structures as sds


class SrepkgCommandInterface(abc.ABC):

    @abc.abstractmethod
    def get_args(self) -> sds.SrepkgCommand:
        pass


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


class ServiceClassBuilderInterface(abc.ABC):

    @abc.abstractmethod
    def build_construction_dir(self, arg) -> ConstructionDirInterface:
        pass


class OrigPkgRetrieverInterface(abc.ABC):

    def __init__(self, orig_pkg_ref: str):
        self._orig_pkg_ref = orig_pkg_ref

    @abc.abstractmethod
    def copy_to_construction_dir(self):
        pass





