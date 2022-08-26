import abc
from pathlib import Path


class OrigPkgReceiver(abc.ABC):

    @property
    @abc.abstractmethod
    def orig_pkg_dists(self) -> Path:
        pass

    @property
    @abc.abstractmethod
    def srepkg_root(self) -> Path:
        pass

    @property
    @abc.abstractmethod
    def srepkg_inner(self) -> Path:
        pass

    @property
    @abc.abstractmethod
    def settle(self):
        pass
