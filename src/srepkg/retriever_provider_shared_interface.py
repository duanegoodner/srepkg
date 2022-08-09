import abc
from pathlib import Path


class OrigPkgReceiver(abc.ABC):

    @property
    @abc.abstractmethod
    def orig_pkg_dest(self) -> Path:
        pass



