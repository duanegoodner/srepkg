import abc
from pathlib import Path


class OrigPkgReceiver(abc.ABC):

    @property
    @abc.abstractmethod
    def orig_pkg_dists(self) -> Path:
        pass



