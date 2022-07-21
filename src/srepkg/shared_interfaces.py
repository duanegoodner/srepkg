import abc


# TODO Move this to Preparer interfaces
class WritableSrepkgDirInterface(abc.ABC):

    @property
    @abc.abstractmethod
    def srepkg_inner(self):
        pass

    @abc.abstractmethod
    def build_missing_items(self):
        pass
