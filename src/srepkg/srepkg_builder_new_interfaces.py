import abc
from pathlib import Path


class SrepkgComponentReceiver(abc.ABC):

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
    def wheel_data(self):
        pass

